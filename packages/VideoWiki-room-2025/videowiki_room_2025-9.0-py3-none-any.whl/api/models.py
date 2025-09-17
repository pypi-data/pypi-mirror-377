# Create your models here.
import os
import random
import xml.etree.ElementTree as ET
#from ast import parse
from hashlib import sha1
from urllib.parse import urlencode
from urllib.request import urlopen
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework.exceptions import ValidationError
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import django.utils.timezone
from dotenv import load_dotenv
import datetime

load_dotenv()
SALT = os.environ.get('SALT_VALUE')
BBB_API_URL = os.environ.get('BBB_API_URL_VALUE')
print("bro", BBB_API_URL)
BASE_URL = os.environ.get('BASE_URL_VALUE')
CLIENT_DOMAIN_URL=os.environ.get('CLIENT_DOMAIN_URL')
CLIENT_DOMAIN_URL_ENV=os.environ.get('CLIENT_DOMAIN_URL_ENV')

def parse(response):
    try:
        xml = ET.XML(response)
        code = xml.find('returncode').text
        if code == 'SUCCESS':
            return xml
        else:
            raise
    except:
        return None


class Meeting(models.Model):
    user_id = models.IntegerField(blank=False)
    event_name = models.CharField(max_length=100)
    event_creator_name = models.CharField(max_length=50)
    event_creator_email = models.CharField(max_length=50)
    private_meeting_id = models.CharField(max_length=100, unique=True)
    public_meeting_id = models.CharField(max_length=100, unique=True)
    meeting_type = models.CharField(max_length=10, blank=True, null=True, default='private')
    attendee_password = models.CharField(max_length=50)
    hashed_attendee_password = models.CharField(max_length=100, null=True, blank=True, default=None)
    moderator_password = models.CharField(max_length=50)
    hashed_moderator_password = models.CharField(max_length=100, null=True, blank=True, default=None)
    viewer_password = models.CharField(max_length=50)
    hashed_viewer_password = models.CharField(max_length=100, null=True, blank=True, default=None)
    viewer_mode = models.BooleanField(default=False, blank=True, null=True)
    moderator_only_text = models.TextField(blank=True, null=True)
    welcome = models.TextField(default='welcome', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    max_participant = models.IntegerField(blank=True, null=True, default=0, validators=[
        MaxValueValidator(1000),
        MinValueValidator(0)
    ])
    record = models.BooleanField(default=False, blank=True, null=True)
    duration = models.IntegerField(default=1000, blank=True, null=True)
    mute_on_start = models.BooleanField(default=True, blank=True, null=True)
    banner_text = models.CharField(max_length=300, blank=True, null=True)
    logo = models.ImageField(blank=True, upload_to='logo_images', null=True)
    guest_policy = models.CharField(max_length=25, default='ALWAYS_ACCEPT', blank=True, null=True)
    end_when_no_moderator = models.BooleanField(default=False, blank=True, null=True)
    allow_moderator_to_unmute_user = models.BooleanField(default=False, null=True, blank=True)
    webcam_only_for_moderator = models.BooleanField(default=False, blank=True, null=True)
    auto_start_recording = models.BooleanField(default=False, blank=True, null=True)
    allow_start_stop_recording = models.BooleanField(default=True, blank=True, null=True)
    disable_cam = models.BooleanField(default=False, null=True, blank=True)
    disable_mic = models.BooleanField(default=False, null=True, blank=True)
    disable_private_chat = models.BooleanField(default=False, null=True, blank=True)
    disable_public_chat = models.BooleanField(default=False, null=True, blank=True)
    disable_note = models.BooleanField(default=False, null=True, blank=True)
    logout_url = models.URLField(blank=True, null=True)
    lock_layout = models.BooleanField(default=False, null=True, blank=True)
    lock_on_join = models.BooleanField(default=True, null=True, blank=True)
    hide_users = models.BooleanField(default=False, null=True, blank=True)
    schedule_time = models.DateTimeField(blank=False, default=django.utils.timezone.now, null=True)
    primary_color = models.CharField(blank=True, max_length=20, null=True)
    secondary_color = models.CharField(blank=True, max_length=20, null=True)
    back_image = models.URLField(blank=True, null=True)
    event_tag = models.CharField(blank=True, max_length=25, null=True)
    schedular_name_reminder = models.CharField(max_length=50)
    cover_image = models.ImageField(blank=True, upload_to='cover_images', null=True)
    is_streaming = models.BooleanField(default=False, null=True, blank=True)
    bbb_resolution = models.CharField(max_length=20, default="1280x720", blank=True, null=True)
    bbb_stream_url_vw = models.TextField(blank=True, null=True)
    raw_time = models.CharField(max_length=100, blank=True, null=True)
    give_nft = models.BooleanField(default=False, null=True, blank=True)
    give_vc = models.BooleanField(default=False, null=True, blank=True)
    send_otp = models.BooleanField(default=False, null=True, blank=True)
    audience_airdrop = models.BooleanField(default=False, blank=True, null=True)
    password_auth = models.BooleanField(default=False, blank=True, null=True)
    public_otp = models.BooleanField(default=False, blank=True, null=True)
    public_nft_flow = models.BooleanField(default=False, blank=True, null=True)
    public_nft_activate = models.BooleanField(default=False, blank=True, null=True)
    public_stream = models.BooleanField(default=False, blank=True, null=True)
    join_count = models.IntegerField(default=0, null=True, blank=True)
    first_room = models.IntegerField(default=False, null=True, blank=True)
    board_id = models.CharField(max_length=100, blank=True, null=True)

    @classmethod
    def api_call(self, query, call):
        prepared = "%s%s%s" % (call, query, SALT)
        checksum = sha1(prepared.encode('utf-8')).hexdigest()
        result = "%s&checksum=%s" % (query, checksum)
        return result

    def is_running(self):
        call = 'isMeetingRunning'
        query = urlencode((
            ('meetingID', self.private_meeting_id),
        ))
        hashed = self.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        result = parse(urlopen(url).read())
        return result.find('running').text

    @classmethod
    def end_meeting(cls, private_meeting_id, password):
        call = 'end'
        query = urlencode((
            ('meetingID', private_meeting_id),
            ('password', password),
        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        result = parse(urlopen(url).read())
        return result

    @classmethod
    def meeting_info(cls, private_meeting_id, password):
        call = 'getMeetingInfo'
        query = urlencode((
            ('meetingID', private_meeting_id),
            ('password', password),
        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        r = parse(urlopen(url).read())
        if r:
            # Create dict of values for easy use in template
            d = {
                'start_time': r.find('startTime').text,
                'end_time': r.find('endTime').text,
                'participant_count': r.find('participantCount').text,
                'moderator_count': r.find('moderatorCount').text,
                'max_users': r.find('maxUsers').text
            }
            return d
        else:
            return None

    @classmethod
    def get_meetings(cls):
        call = 'getMeetings'
        query = urlencode((
            ('random', 'random'),
        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        result = parse(urlopen(url).read())
        print(result)
        if result:
            # Create dict of values for easy use in template
            d = []
            r = result[1].findall('meeting')
            for m in r:
                name = m.find('meetingName').text
                password = m.find('moderatorPW').text
                meeting_id = m.find('meetingID').text
                d.append({
                    'name': name,
                    'running': m.find('running').text,
                    'info': Meeting.meeting_info(
                        meeting_id,
                        password)
                })
            return d

    def start(self, code):
        call = 'create'
        voicebridge = 70000 + random.randint(0, 9999)
        meeting_url =  CLIENT_DOMAIN_URL + "e/{}/".format(self.public_meeting_id)
  #      shortcode = URL.objects.filter(room_id=i.public_meeting_id).first()
        if self.user_id == 0:
            moderator_url = CLIENT_DOMAIN_URL + "/e/{}/?pass={}".format(self.public_meeting_id,self.hashed_moderator_password)
            participant_url = CLIENT_DOMAIN_URL + "/e/{}/?pass={}".format(self.public_meeting_id,self.hashed_attendee_password)
        elif self.meeting_type == 'private':
            moderator_url = meeting_url + f"?email=your-email"
            participant_url = meeting_url + f"?email=your-email"
        else:
            participant_url = CLIENT_DOMAIN_URL + "e/{}/?pass={}".format(self.public_meeting_id,
                                                                          self.hashed_attendee_password)
            moderator_url = CLIENT_DOMAIN_URL + "e/{}/?pass={}".format(self.public_meeting_id,
                                                                        self.hashed_moderator_password)

        tuple_1 = (
            ('name', self.event_name),
            ('meetingID', self.private_meeting_id),
            ('attendeePW', self.attendee_password),
            ('moderatorPW', self.moderator_password),
            ('voiceBridge', voicebridge),
            ('moderatorOnlyMessage', self.moderator_only_text),
            ('welcome', self.welcome),
            ('maxParticipants', self.max_participant),
            ('record', self.record),
            ('duration', self.duration),
            ('logoutURL', self.logout_url),
            ('muteOnStart', self.mute_on_start),
            ('logo', str(path_getter(self.logo))),
            ('endWhenNoModerator', self.end_when_no_moderator),
            ('guestPolicy', self.guest_policy),
            ('allowModsToUnmuteUsers', self.allow_moderator_to_unmute_user),
            ('webcamsOnlyForModerator', self.webcam_only_for_moderator),
            ('autoStartRecording', self.auto_start_recording),
            ('allowStartStopRecording', self.allow_start_stop_recording),
            ('lockSettingsDisableCam', self.disable_cam),
            ('lockSettingsDisableMic', self.disable_mic),
            ('lockSettingsDisableNote', self.disable_note),
            ('lockSettingsDisablePrivateChat', self.disable_public_chat),
            ('lockSettingsDisablePublicChat', self.disable_private_chat),
            ('lockSettingsLockedLayout', self.lock_layout),
            ('lockSettingsLockOnJoin', self.lock_on_join),
            ('lockSettingsHideUserList', self.hide_users),
            ('meta_bbb-origin', 'Greenlight'),
            ('meta_bbb-origin-version', "v2"),
            ('meta_bbb-origin-server-name', 'room.video.wiki'),
            ('meta_primary-color', self.primary_color),
            ('meta_secondary-color', self.secondary_color),
            ('meta_back-image', str(path_getter1(self.cover_image))),
            ('meta_gl-listed', False),
#            ('meta_participantUrl', participant_url),
#            ('meta_pmoderatorUrl', moderator_url),
            ('meta_participantUr', CLIENT_DOMAIN_URL_ENV + "/j/{}/".format(code))
        )
        tuple_2 = ('bannerText', self.banner_text)
        if self.banner_text == None:
            f_tuple = tuple_1
        else:
            tuple_1_list = list(tuple_1)
            tuple_1_list.append(tuple_2)
            f_tuple = tuple(tuple_1_list)
        query = urlencode(f_tuple)
        hashed = self.api_call(query, call)
        print(BBB_API_URL,"lll")
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        result = parse(urlopen(url).read())
        return result

    @classmethod
    def join_url(cls, meeting_id, name, password, force_listen_only, enable_screen_sharing, enable_webcam):
        call = 'join'
        query = urlencode((
            ('meetingID', meeting_id),
            ('password', password),
            ('fullName', name),
            ('userdata-bbb_force_listen_only', force_listen_only),
            ('bbb_enable_screen_sharing', enable_screen_sharing),
            ('userdata-bbb_enable_video', enable_webcam)
        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        return url

    @classmethod
    def get_recordings(cls, private_meeting_id, pid):
        call = "getRecordings"
        query = urlencode((
            ('meetingID', private_meeting_id),
        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        response = urlopen(url)
        result = response.read()  # Read the response content as bytes

        # Parse the XML response
        root = ET.fromstring(result.decode())  # Decode the bytes to a string

        # Extract data from the XML elements
        returncode = root.find("returncode").text
        recordings = root.find("recordings")

        if recordings:
            recording_elements = recordings.findall("recording")
            recording_data = []

            for recording in recording_elements:
                record_id = recording.find("recordID").text
                meeting_id = recording.find("meetingID").text
                internal_meeting_id = recording.find("internalMeetingID").text
                name = recording.find("name").text
                is_breakout = recording.find("isBreakout").text
                published = recording.find("published").text
                state = recording.find("state").text
                start_time = int(recording.find("startTime").text) // 1000  # Convert to seconds
                end_time = int(recording.find("endTime").text) // 1000  # Convert to seconds
                participants = recording.find("participants").text
                raw_size = int(recording.find("rawSize").text)  # Convert to integer
                # Extract metadata if available
                metadata = recording.find("metadata")
                if metadata is not None:
                    meta_name = metadata.find("name")
                    if meta_name is not None and meta_name.text:
                        name = meta_name.text

                # Convert timestamps to readable format
                start_time_readable = datetime.datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S UTC')
                end_time_readable = datetime.datetime.utcfromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S UTC')

                # Extract additional data as needed

                # Extract playback data if available
                playback = recording.find("playback")
                if playback is not None:
                    playback_format = playback.find("format")
                    playback_type = playback_format.find("type").text
                    playback_url = playback_format.find("url").text
                    playback_processing_time = int(playback_format.find("processingTime").text)
                    playback_length = int(playback_format.find("length").text)
                    playback_size = int(playback_format.find("size").text)

                    # Convert playback size to human-readable format
                    playback_size_readable = cls.human_readable_size(playback_size)

                    playback_data = {
                        "Playback Type": playback_type,
                        "Playback URL": playback_url.strip(),
                        "Playback Processing Time": playback_processing_time,
                        "Playback Length": playback_length,
                        "Playback Size": playback_size_readable,
                    }
                else:
                    playback_data = None

                recording_data.append({
                    "Record ID": record_id,
                    "Meeting ID": meeting_id,
                    "Internal Meeting ID": internal_meeting_id,
                    "Name": name,
                    "Is Breakout": is_breakout,
                    "Published": published,
                    "State": state,
                    "Start Time (Readable)": start_time_readable,
                    "End Time (Readable)": end_time_readable,
                    "Participants": participants,
                    "Raw Size": raw_size,
                    "pub_id": pid,
                    "Playback Data": playback_data
                })

            return recording_data

        else:
            print("No recordings found in the response.")
            return None
    @classmethod
    def update_recordings(cls, record_id, name):
        call = "updateRecordings"
        query = urlencode((
            ('recordID', record_id),
            ('meta_name', name),

        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        response = urlopen(url)
        result = response.read()  # Read the response content as bytes
        # Parse the XML response
        root = ET.fromstring(result.decode())  # Decode the bytes to a string
        # print(response, response.text, root)
        result = parse(urlopen(url).read())
        return result

    @classmethod
    def delete_recording(cls, record_id):
        call = 'deleteRecordings'
        query = urlencode((
            ('recordID', record_id),
        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        result = parse(urlopen(url).read())
        if result == None:
            return "already deleted"

        return result.find('deleted').text

    @staticmethod
    def human_readable_size(size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f} {unit}"

    @classmethod
    def is_meeting_running(cls, private_meeting_id):
        call = 'isMeetingRunning'
        query = urlencode((
            ('meetingID', private_meeting_id),
        ))
        hashed = cls.api_call(query, call)
        url = BBB_API_URL + 'api/' + call + '?' + hashed
        result = parse(urlopen(url).read())
        return result.find('running').text


def path_getter(path):
    if path == "https://decaststorage.blob.core.windows.net/room-db-backup/decasticon.svg":
        url = path
    elif path == "https://decaststorage.blob.core.windows.net/room-db-backup/Cast-Draft-Logo-02.png":
        url = "https://decaststorage.blob.core.windows.net/room-db-backup/decasticon.svg"
    else:
        url = BASE_URL + path.url
    return url

def path_getter1(path):
    return str(path)


def generate_random_key(self):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(8, chars)
    return secret_key


def user_info(token):
    data = {'token': token}
    try:
        valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
        user_id = valid_data['user_id']
        return user_id

    except ValidationError as v:
        return -1


def user_info_email(token):
    data = {'token': token}
    try:
        valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
        email = valid_data['email']
        return email

    except ValidationError as v:
        return -1


def user_info_name(token):
    data = {'token': token}
    try:
        valid_data = TokenBackend(algorithm='HS256').decode(token, verify=False)
        name = valid_data['username']
        return name

    except ValidationError as v:
        return -1
