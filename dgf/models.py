import logging
import re
from decimal import Decimal

from cms.models import User, CMSPlugin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Model
from django.db.models.deletion import CASCADE, SET_NULL
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from partial_date import PartialDateField

from dgf.post_actions import feedback_post_save

logger = logging.getLogger(__name__)

MAX_AMOUNT_OF_HIGHLIGHTS = 5


class Division(Model):
    """
    This needs to be filled with content from the PDGA:
    https://www.pdga.com/pdga-documents/tour-documents/divisions-ratings-and-points-factors
    """

    id = models.CharField(_('ID'), max_length=10, primary_key=True)
    text = models.CharField(_('Text'), max_length=100)

    def __str__(self):
        return self.text


class Course(Model):
    """
    This needs to be filled with content. Initially we provided a fixture (courses_de.json)
    If needed, more models will be added via django admin
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'postal_code', 'country'], name='unique_course'),
        ]

    name = models.CharField(_('Name'), max_length=100)
    postal_code = models.CharField(_('Postal code'), max_length=10)
    city = models.CharField(_('City'), max_length=50)
    country = CountryField(_('Country'))
    udisc_id = models.CharField(_('UDisc ID'), max_length=100, null=True, blank=True)
    udisc_main_layout = models.CharField(_('Main Layout'), max_length=100, null=True, blank=True)

    def __str__(self):
        if self._contain_each_other(self.name, self.city):
            if self.country == 'DE':
                place = ''
            else:
                place = f' ({self.country})'
        else:
            if self.country == 'DE':
                place = f' ({self.city})'
            else:
                place = f' ({self.city}, {self.country})'

        return f'{self.name}{place}'

    def _contain_each_other(self, a, b):
        words_a = self._words_of(a)
        words_b = self._words_of(b)
        return len(words_a.intersection(words_b)) > 0

    @staticmethod
    def _words_of(string):
        return set(re.findall('\w+', string))


class CoursePluginModel(CMSPlugin):
    course = models.ForeignKey(Course, on_delete=CASCADE)

    def __str__(self):
        return str(self.course)


class Friend(User):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_slug'),
            models.UniqueConstraint(fields=['pdga_number'], name='unique_pdga_number'),
            models.UniqueConstraint(fields=['gt_number'], name='unique_gt_number'),
        ]

    nickname = models.CharField(_('Nickname'), max_length=30, null=True, blank=True)
    club_role = models.CharField(_('Club role'), max_length=200, null=True, blank=True)

    sponsor = models.CharField(_('Sponsor'), max_length=200, null=True, blank=True)
    sponsor_logo = models.ImageField(_('Sponsor logo'), null=True, blank=True)
    sponsor_link = models.URLField(_('Sponsor link'), null=True, blank=True)

    udisc_username = models.CharField(_('UDisc Username'), max_length=100, null=True, blank=True)
    pdga_number = models.PositiveIntegerField(_('PDGA Number'), null=True, blank=True)
    gt_number = models.PositiveIntegerField(_('GT Number'), null=True, blank=True)
    division = models.ForeignKey(Division, null=True, blank=True, on_delete=SET_NULL, verbose_name=_('Division'))
    city = models.CharField(_('City'), max_length=100, null=True, blank=True)
    main_photo = models.ImageField(_('Main photo'), null=True, blank=True)
    plays_since = models.PositiveIntegerField(_('Plays since'), null=True, blank=True,
                                              validators=[MinValueValidator(1926)])
    best_score_in_wischlingen = models.IntegerField(_('Best score in Wischlingen (relative to par)'), null=True,
                                                    blank=True)
    free_text = models.TextField(_('Started playing'), null=True, blank=True)
    job = models.CharField(_('Job'), max_length=200, null=True, blank=True)
    hobbies = models.CharField(_('Other hobbies'), max_length=200, null=True, blank=True)

    slug = models.SlugField(_('Slug'), max_length=30, null=True, blank=True)
    rating = models.PositiveIntegerField(_('Rating'), null=True, blank=True, validators=[
        MaxValueValidator(2000)
    ])
    total_tournaments = models.PositiveIntegerField(_('Total tournaments'), null=True, blank=True, default=0)
    total_earnings = models.DecimalField(_('Total earnings'), max_digits=10, decimal_places=2, default=Decimal(0.00))

    @property
    def full_name(self):
        nickname = f' ({self.nickname})' if self.nickname else ''
        return f'{self.first_name} {self.last_name}{nickname}'

    @property
    def short_name(self):
        return self.nickname or self.first_name

    @property
    def initials(self):
        first = self.first_name[0] if self.first_name else ''
        second = self.last_name[0] if self.last_name else ''
        return f'{first} {second}'

    def __str__(self):
        pdga_number = f' #{self.pdga_number}' if self.pdga_number else ''
        return f'{self.first_name} {self.last_name}{pdga_number}'

    def save(self, *args, **kwargs):
        new_slug = self.slug or self.nickname or self.first_name or self.username
        self.slug = slugify(new_slug).lower()
        logger.info(f'Setting slug for {self.username} to {self.slug}')
        super(Friend, self).save(*args, **kwargs)


class UdiscRound(Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'friend'],
                                    name='Only one score per course and friend allowed. The best one'),
        ]

    course = models.ForeignKey(Course, on_delete=CASCADE)
    friend = models.ForeignKey(Friend, on_delete=CASCADE)
    score = models.IntegerField(_('Last score from UDisc'))

    def __str__(self):
        return f'{self.friend} scored {self.score} in {self.course}'


class FavoriteCourse(Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'friend'], name='the same course can not be favorite twice'),
        ]

    course = models.ForeignKey(Course, on_delete=CASCADE, related_name='favorites', verbose_name=_('Course'))
    friend = models.ForeignKey(Friend, on_delete=CASCADE, related_name='favorite_courses', verbose_name=_('Friend'))

    def __str__(self):
        return str(self.course)


class Feedback(Model):
    title = models.CharField(_('Title'), max_length=200)
    feedback = models.TextField(_('Feedback'), )
    friend = models.ForeignKey(Friend, null=True, on_delete=CASCADE, verbose_name=_('Friend'))

    def __str__(self):
        return f'{self.friend.short_name if self.friend else None} - {self.title}'

    def save(self, *args, **kwargs):
        super(Feedback, self).save(*args, **kwargs)
        try:
            feedback_post_save(self)
        except:
            logger.warning('I could not create this feedback as an issue in Github!')


class Highlight(Model):
    content = models.CharField(_('Content'), max_length=100)
    friend = models.ForeignKey(Friend, on_delete=CASCADE, related_name='highlights')

    def __str__(self):
        return str(self.content)


class FriendPluginModel(CMSPlugin):
    friend = models.ForeignKey(Friend, on_delete=CASCADE)

    def __str__(self):
        return str(self.friend)


class Disc(models.Model):
    manufacturer = models.CharField(_('Manufacturer'), max_length=200, null=True, blank=True)
    mold = models.CharField(_('Mold'), max_length=200, unique=True)
    display_name = models.CharField(_('Display name'), max_length=200)

    def __str__(self):
        return f'{self.mold} [{self.manufacturer}]'

    def save(self, *args, **kwargs):
        self.display_name = re.sub(' *\(.*\)', '', self.mold)
        super(Disc, self).save(*args, **kwargs)


class DiscInBag(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['disc', 'friend'], name='unique_disc_for_friend'),
        ]

    PUTTER = 'P'
    MID_RANGE = 'M'
    FAIRWAY_DRIVER = 'F'
    DISTANCE_DRIVER = 'D'
    TYPE_CHOICES = (
        (PUTTER, _('Putter')),
        (MID_RANGE, _('Mid-range')),
        (FAIRWAY_DRIVER, _('Fairway driver')),
        (DISTANCE_DRIVER, _('Distance driver')),
    )
    type = models.CharField(_('Type'), max_length=1, choices=TYPE_CHOICES)
    amount = models.PositiveIntegerField(_('Amount'), default=1, validators=[MinValueValidator(1)])
    disc = models.ForeignKey(Disc, on_delete=CASCADE, related_name='bags', verbose_name=_('Disc'))
    friend = models.ForeignKey(Friend, on_delete=CASCADE, related_name='discs', verbose_name=_('Player'))

    @property
    def in_the_bag(self):
        count = '' if self.amount == 1 else f'{self.amount}x '
        return f'{count}{self.disc.display_name}'

    def __str__(self):
        return f'{self.amount}x {self.disc.mold} ({self.get_type_display()})'


class Ace(models.Model):
    PRACTICE = 'P'
    CASUAL_ROUND = 'C'
    TOURNAMENT = 'T'
    TYPE_CHOICES = (
        (PRACTICE, _('Practice')),
        (CASUAL_ROUND, _('Casual Round')),
        (TOURNAMENT, _('Tournament')),
    )
    friend = models.ForeignKey(Friend, on_delete=CASCADE, related_name='aces')
    disc = models.ForeignKey(Disc, null=True, on_delete=SET_NULL, related_name='aces', verbose_name=_('Disc'))
    course = models.ForeignKey(Course, null=True, on_delete=SET_NULL, related_name='aces', verbose_name=_('Course'))
    hole = models.CharField(_('Hole'), max_length=20)
    type = models.CharField(_('Type'), max_length=1, choices=TYPE_CHOICES)
    date = PartialDateField(_('Date'), null=True, blank=True)

    def __str__(self):
        date = f' - {self.date}' if self.date else ''
        return f'{self.course} - ' \
               f'{_("Hole")} {self.hole} ' \
               f'{_("with a")} {self.disc.display_name} ' \
               f'[{self.get_type_display()}]{date}'


class Video(Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['url', 'friend'], name='unique_video_for_friend'),
        ]

    IN_THE_BAG = 'B'
    ACE = 'A'
    OTHER = 'O'
    TYPE_CHOICES = (
        (IN_THE_BAG, _('In the bag')),
        (ACE, _('Ace')),
        (OTHER, _('Other')),
    )
    type = models.CharField(_('Type'), max_length=1, choices=TYPE_CHOICES, default=OTHER)
    url = models.URLField(_('URL'), )
    friend = models.ForeignKey(Friend, on_delete=CASCADE, related_name='videos')

    def __str__(self):
        return str(self.url)


class Tournament(models.Model):
    begin = models.DateField(auto_now=False, auto_now_add=False)
    end = models.DateField(auto_now=False, auto_now_add=False)
    name = models.CharField(_('Name'), max_length=300)

    @property
    def date(self):
        if self.begin == self.end:
            return self.begin.strftime('%d. %b %Y')

        if self.begin.month != self.end.month:
            begin = self.begin.strftime('%d. %b')
            end = self.end.strftime('%d. %b %Y')
        else:
            begin = self.begin.strftime('%d.')
            end = self.end.strftime('%d. %b %Y')

        return f'{begin} - {end}'

    def __str__(self):
        return f'{self.name} ({self.date})'


class Attendance(Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tournament', 'friend'],
                                    name='the same tournament can not be attended twice'),
        ]

    tournament = models.ForeignKey(Tournament, on_delete=CASCADE, related_name='attendance',
                                   verbose_name=_('Tournament'))
    friend = models.ForeignKey(Friend, on_delete=CASCADE, related_name='attendance', verbose_name=_('Player'))

    def __str__(self):
        return f'{self.tournament} - {self.friend}'
