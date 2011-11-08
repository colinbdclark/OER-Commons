from django.core.management.base import NoArgsCommand
import copy, datetime, logging, os, shlex, subprocess, simplejson


logger = logging.getLogger("rubrics.publish_evaluations_to_lr")


class Command(NoArgsCommand):

    help = "Upload resource evaluation data to Learning Registry network. This command uploads the data for the previous month. It is supposed to run as cron job on 1st of each month."

    def handle_noargs(self, **options):
        from django.conf import settings
        from django.contrib.sites.models import Site
        from django.core.exceptions import ImproperlyConfigured
        from django.db.models import Avg
        from curriculum.models import AlignmentTag
        from rubrics.models import Evaluation, StandardAlignmentScore, RubricScore, Rubric

        command = getattr(settings, "LR_COMMAND")
        if not command:
            raise ImproperlyConfigured("LR_COMMAND is not specified.")

        key = getattr(settings, "LR_KEY")
        if not key:
            raise ImproperlyConfigured("LR_KEY is not specified.")

        key_location = getattr(settings, "LR_KEY_LOCATION")
        if not key_location:
            raise ImproperlyConfigured("LR_KEY_LOCATION is not specified.")

        passphrase = getattr(settings, "LR_PASSPHRASE")
        if not passphrase:
            raise ImproperlyConfigured("LR_PASSPHRASE is not specified.")

        node = getattr(settings, "LR_NODE")
        if not node:
            raise ImproperlyConfigured("LR_NODE is not specified.")

        publish_url = os.path.join(node, "publish")

        args = shlex.split(command) + ["--key", key,
                                       "--key-location", key_location,
                                       "--passphrase", passphrase,
                                       "--publish-url", publish_url]

        username = getattr(settings, "LR_NODE_USERNAME", None)
        password = getattr(settings, "LR_NODE_PASSWORD", None)

        if username and password:
            args += [
                "--publish-username", username,
                "--publish-password", password,
            ]

        ENVELOPE = {
            "TOS": {
                "submission_TOS": "http://www.learningregistry.org/tos/cc0/v0-5/"
            },
            "active": True,
            "doc_type": "resource_data",
            "doc_version": "0.23.0",
            "identity": {
                "submitter": "OER Commons",
                "submitter_type": "agent"
            },
            "payload_placement": "inline",
            "payload_schema": ["LR Paradata 1.0"],
            "keys": [],
            "resource_data": {
                "activity": {
                    "verb": {
                        "action": "rated",
                        "measure": {
                            "value": None,
                            "scaleMin": 0,
                            "scaleMax": 3,
                            "sampleSize": None,
                        },
                        "date": None
                    },
                    "object": None,
                    "related": None
                },
            },
            "resource_data_type": "paradata",
            "resource_locator": None
        }

        today = datetime.date.today()
        until_date = today.replace(day=1) - datetime.timedelta(days=1)
        from_date = until_date.replace(day=1)

        evaluations = Evaluation.objects.filter(
            timestamp__gte=from_date,
            timestamp__lte=until_date,
            confirmed=True
        )
        evaluation_number = evaluations.count()

        site_url = "http://%s" % Site.objects.get_current().domain

        for evaluation in evaluations:
            instance = evaluation.content_object
            if hasattr(instance, "get_absolute_url"):
                url = site_url + instance.get_absolute_url()
            elif hasattr(instance, "url"):
                url = instance.url
            else:
                continue

            for row in StandardAlignmentScore.objects.filter(
                evaluation=evaluation,
            ).exclude(score__value=None).values("alignment_tag").distinct().annotate(
                avg_score=Avg("score__value")
            ):
                tag = AlignmentTag.objects.get(id=row["alignment_tag"])
                message = copy.deepcopy(ENVELOPE)
                message["resource_locator"] = url
                message["resource_data"]["activity"]["object"] = url
                message["resource_data"]["activity"]["verb"]["measure"]["value"] = row["avg_score"]
                message["resource_data"]["activity"]["verb"]["measure"]["sampleSize"] = evaluation_number
                message["resource_data"]["activity"]["verb"]["date"] = "%s/%s" % (
                    from_date.strftime("%Y-%m-%d"),
                    until_date.strftime("%Y-%m-%d"),
                )
                message["resource_data"]["activity"]["related"] = [
                    {"object": {
                        "type": "Common Core Standard",
                        "description": tag.full_code,
                    }}
                ]

                message = simplejson.dumps(message, indent=2)

                logger.debug(message)

                process = subprocess.Popen(args,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

                out, err = process.communicate(message)

                if out:
                    logger.info(out)

                if err:
                    logger.error(err)


            for row in RubricScore.objects.filter(
                evaluation=evaluation,
            ).exclude(score__value=None).values("rubric").distinct().annotate(
                avg_score=Avg("score__value")
            ):

                rubric = Rubric.objects.get(id=row["rubric"])
                message = copy.deepcopy(ENVELOPE)
                message["resource_locator"] = url
                message["resource_data"]["activity"]["object"] = url
                message["resource_data"]["activity"]["verb"]["measure"]["value"] = row["avg_score"]
                message["resource_data"]["activity"]["verb"]["measure"]["sampleSize"] = evaluation_number
                message["resource_data"]["activity"]["verb"]["date"] = "%s/%s" % (
                    from_date.strftime("%Y-%m-%d"),
                    until_date.strftime("%Y-%m-%d"),
                )
                message["resource_data"]["activity"]["related"] = [
                    {"object": {
                        "type": "OER Rubric",
                        "description": rubric.name,
                    }}
                ]

                message = simplejson.dumps(message, indent=2)

                logger.debug(message)

                process = subprocess.Popen(args,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

                out, err = process.communicate(message)

                if out:
                    logger.info(out)

                if err:
                    logger.error(err)
