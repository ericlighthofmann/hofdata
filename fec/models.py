from django.db import models
from django.http import Http404

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.core.blocks import StreamBlock
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailcodeblock.blocks import CodeBlock

class Candidate(models.Model):

    name = models.CharField(max_length=255)
    candidate_id = models.CharField(max_length=255, blank=True)
    candidate_status = models.CharField(max_length=5, blank=True)
    district = models.CharField(max_length=2, blank=True)
    incumbent_challenge_status = models.CharField(max_length=55, blank=True, null=True)
    party = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=2, blank=True)

# WAGTAIL PAGE MODELS
class FECSummaryPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        if not context['request'].user.is_superuser:
            raise Http404("You\'re not allowed here buckaroo!")
        candidates = Candidate.objects.all()
        context['candidates'] = candidates
        return context
