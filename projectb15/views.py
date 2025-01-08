from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import Group, User
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from .models import Event, Upload, Message
from users.models import Profile
from .forms import FileUploadForm, CreateMessageForm, AddEventForm
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from datetime import datetime, timedelta, date
from django.utils import timezone
from django.contrib import messages

# Utility Functions
def create_groups():
    """Create default groups if they don't exist."""
    if not Group.objects.filter(name="User"):
        Group.objects.create(name="User")
    if not Group.objects.filter(name="Admin"):
        Group.objects.create(name="Admin")

# Views
def home(request):
    """Home page view."""
    if Group.objects.count() < 2:
        create_groups()
    user = request.user
    if user.is_authenticated and not user.groups.exists():
        user.groups.add(Group.objects.get(name="User"))
    
    date2 = date.today()
    start_week = date2 - timedelta(date2.weekday())
    end_week = start_week + timedelta(7)
    events_this_week = None
    invites = None
    
    if 'accept_button' in request.POST:
            event_id = request.POST.get('event_id')
            event_obj = Event.objects.get(pk=event_id)
            event_obj.invited.remove(user)
            event_obj.members.add(user)
            print('accept')
            event_obj.save()
    if 'reject_button' in request.POST:
            event_id = request.POST.get('event_id')
            event_obj = Event.objects.get(pk=event_id)
            event_obj.invited.remove(user)
            event_obj.save()
            
    if user.is_authenticated:
        owned_events = Event.objects.filter(owner=user, date__range=[date2, end_week]) 
        member_events = Event.objects.filter(members=user, date__range = [date2, end_week])
        events_this_week = owned_events | member_events

        invites = Event.objects.filter(invited=user)
        
    return render(request, "index.html", {'events_this_week': events_this_week, 'invites': invites})


@login_required
def post_login_redirect(request):
    """Redirect logged-in users to the home page."""
    Profile.objects.get_or_create(user=request.user)  # Ensure the profile exists
    return redirect('home')


class CustomLoginView(LoginView):
    """Custom login view."""
    template_name = 'registration/login.html'
    success_url = reverse_lazy('home')

    def get_success_url(self):
        # Ensure profile exists, but no need to redirect to a nickname route
        Profile.objects.get_or_create(user=self.request.user)
        return super().get_success_url()

# Event Views
class EventsListView(generic.ListView):
    """List view for user's events."""
    model = Event
    context_object_name = 'event_list'
    template_name = 'event_list.html'

    def get_queryset(self):
        today = now().date()

        owned_events = Event.objects.filter(owner=self.request.user)
        member_events = Event.objects.filter(members=self.request.user)
        all_events = owned_events | member_events

        past_events = all_events.filter(date__lt=today)
        upcoming_events = all_events.filter(date__gte=today)

        return {
            'past_events': past_events,
            'upcoming_events': upcoming_events
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_queryset())  # Add past and upcoming events to context
        return context


class PublicEventsListView(generic.ListView):
    """List view for public events."""
    model = Event
    context_object_name = 'event_list'
    template_name = 'public_event_list.html'

    def get_queryset(self):
        today = now().date()

        all_events = Event.objects.exclude(visibility=2)

        past_events = all_events.filter(date__lt=today)
        upcoming_events = all_events.filter(date__gte=today)

        return {
            'past_events': past_events,
            'upcoming_events': upcoming_events
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_queryset())  # Add past and upcoming events to context
        return context

class AdminEventList(generic.ListView):
    """List view for all events (admin only)."""
    model = Event
    context_object_name = 'event_list'
    template_name = 'admin_event_list.html'


class EventDetail(FormMixin, generic.DetailView):
    template_name = 'projectb15/event_detail.html'
    model = Event
    form_class = FileUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = Upload.objects.filter(event=self.object)
        context['event_messages'] = Message.objects.filter(event=self.object)

        # Calculate the duration in a user-friendly format
        if self.object.start_time and self.object.end_time:
            start_datetime = datetime.combine(self.object.date, self.object.start_time)
            end_datetime = datetime.combine(self.object.date, self.object.end_time)
            duration = end_datetime - start_datetime

            if duration.days > 0:
                context['event_duration'] = f"{duration.days} day{'s' if duration.days != 1 else ''}, {duration.seconds // 3600} hour{'s' if duration.seconds // 3600 > 1 else ''}, {(duration.seconds % 3600) // 60} minute{'s' if (duration.seconds % 3600) // 60 > 1 else ''}"
            else:
                context['event_duration'] = f"{duration.seconds // 3600} hour{'s' if duration.seconds // 3600 != 1 else ''}, {(duration.seconds % 3600) // 60} minute{'s' if (duration.seconds % 3600) // 60 > 1 else ''}"
        else:
            context['event_duration'] = None  # No valid duration

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if request.method == 'POST' and 'join_button' in request.POST:
            event = self.get_object()
            related_object = User.objects.get(username=self.request.user.username)
            event.pending_invites.add(related_object)
            messages.success(request, "Your request has been sent.")
            event.save() 
            return redirect('event-detail', pk = self.kwargs['pk'])
        if 'message_button' in request.POST:
            if request.POST.get('content'):
                message = Message()
                message.event_id = self.kwargs['pk']
                text = request.POST.get('content')
                message.content = text
                message.poster_id = User.objects.get(username=self.request.user.username).id
                message.save()
                return redirect('event-detail', pk = self.kwargs['pk'])
        
        if 'invite_button' in request.POST:
            username = request.POST.get('invite_username')
            try:
                user_to_invite = User.objects.get(username=username)
                if user_to_invite in self.object.members.all():
                    invite_form_error = f"{username} is already a member."
                elif user_to_invite in self.object.pending_invites.all():
                    invite_form_error = f"{username} has already been invited."
                elif user_to_invite == self.object.owner:
                    invite_form_error = f"You are the owner of this event."
                else:
                    # Add the user as a member
                    self.object.invited.add(user_to_invite)
                    messages.success(request, "Your invitation has been sent.")
                    self.object.save()
                    invite_form_error = None  # Clear any error
                    return self.render_to_response(self.get_context_data(invite_form_error=None))

            except User.DoesNotExist:
                invite_form_error = f"User {username} does not exist."

            # Return the page with an error message
            return self.render_to_response(self.get_context_data(invite_form_error=invite_form_error))
        if 'reject_button' in request.POST:
            username = request.POST.get('your_name')
            user = User.objects.get(username=username)
            self.object.pending_invites.remove(user)
            self.object.save()
            return self.render_to_response(self.get_context_data(invite_message=f"{username}'s request has been rejected"))
        
        if 'accept_button' in request.POST:
            username = request.POST.get('your_name')
            user = User.objects.get(username=username)
            self.object.pending_invites.remove(user)
            self.object.members.add(user)
            self.object.save()
            return self.render_to_response(self.get_context_data(invite_message=f"{username} has been added as a member"))
       
        if 'delete_file' in request.POST:
            file_id = request.POST.get('file_id')  
            file_obj = Upload.objects.get(id=file_id)  
            event_obj = self.get_object()
            file_obj.delete()
        
        if 'message_delete' in request.POST:
            message_id = request.POST.get('message_id')
            message_obj = Message.objects.get(id=message_id)
            message_obj.delete()
            
        # Handle the remove member functionality
        if 'remove_button' in request.POST:
            username = request.POST.get('remove_username')
            try:
                user_to_remove = User.objects.get(username=username)
                if user_to_remove in self.object.members.all():
                    self.object.members.remove(user_to_remove)
                    self.object.save()
                    return self.render_to_response(self.get_context_data(invite_form_error=None))
                else:
                    invite_form_error = f"User {username} is not a member of this event."
            except User.DoesNotExist:
                invite_form_error = f"User {username} does not exist."

            # Return the page with an error message
            return self.render_to_response(self.get_context_data(invite_form_error=invite_form_error))

        # Handle other buttons (e.g., join, accept, etc.)
        return self.render_to_response(self.get_context_data())


    def get_success_url(self):
        return reverse('event-detail', kwargs={'pk': self.object.id})


class EventCreate(CreateView):
    model = Event
    form_class = AddEventForm
    template_name = 'create_project.html'

    def form_valid(self, form):
        event = form.save(commit=False)
        event.owner = self.request.user  # Assign the current user as the owner
        
        # Debugging: Print file details
        header_image = form.cleaned_data.get('header_image')
        if header_image:
            print(f"File uploaded: {header_image.name}")
        else:
            print("No file uploaded for header_image.")
        
        event.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        # Log form errors (optional for debugging)
        for field, errors in form.errors.items():
            print(f"{field}: {errors}")
        # Re-render the form with validation errors
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse('events')  # Redirect to the events list or any other page


class EventUpdate(UpdateView):
    model = Event
    form_class = AddEventForm
    template_name = 'edit_event.html'

    def get_success_url(self):
        return reverse('event-detail', kwargs={'pk': self.object.pk})  # Redirect to the event details page


class EventDelete(DeleteView):
    """View to delete an event."""
    model = Event
    success_url = reverse_lazy('events')

@method_decorator(login_required, name='dispatch')
class InvitesListView(generic.ListView):
    """List view for pending event invites."""
    model = Event
    template_name = 'invites_list.html'  # Ensure this template exists
    context_object_name = 'invites'

    def get_queryset(self):
        # Filter events where the user is in pending invites
        return Event.objects.filter(pending_invites=self.request.user)

    def post(self, request, *args, **kwargs):
        # Handle accept/reject actions
        if 'action' in request.POST:
            event_id = request.POST.get('event_id')
            action = request.POST.get('action')

            if event_id:
                event = Event.objects.get(pk=event_id)

                if action == 'accept':
                    event.pending_invites.remove(request.user)
                    event.members.add(request.user)
                elif action == 'reject':
                    event.pending_invites.remove(request.user)
                event.save()

        return redirect('invites')

# File Views
class ManageFilesList(generic.ListView):
    """List view for managing files associated with an event."""
    model = Upload
    context_object_name = 'files'

    def get_queryset(self):
        return Upload.objects.filter(event=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        if 'delete_button' in request.POST:
            event_obj = Event.objects.get(pk=self.kwargs['pk'])
            Upload.objects.filter(event=event_obj).delete()
            return HttpResponseRedirect(reverse("manage-files", kwargs={"pk": self.kwargs['pk']}))
        return super().post(request, *args, **kwargs)


def upload_file(request, pk):
    """View to handle file uploads."""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.event = get_object_or_404(Event, pk=pk)
            file.save()
            return redirect('event-detail', pk=pk)
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})


def file_list(request):
    """View to list all files."""
    files = Upload.objects.all()
    return render(request, 'file_list.html', {'files': files})


# Message Views
class MessagesListView(FormMixin, generic.ListView):
    """List view for event messages."""
    model = Message
    context_object_name = 'messages_list'
    form_class = CreateMessageForm
    template_name = 'messages_list.html'

    def get_queryset(self):
        return Message.objects.filter(event=self.kwargs['pk'])

    def form_valid(self, form):
        message = form.save(commit=False)
        message.event_id = self.kwargs['pk']
        message.poster = self.request.user
        message.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("events")
