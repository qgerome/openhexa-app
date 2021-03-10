# Generated by Django 3.1.6 on 2021-03-10 09:24

from django.db import migrations, models
import django.db.models.deletion
import habari.common.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dhis2IndicatorType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("external_id", models.CharField(max_length=100, unique=True)),
                ("dhis2_name", models.CharField(max_length=200)),
                ("dhis2_short_name", models.CharField(blank=True, max_length=100)),
                ("dhis2_description", models.TextField(blank=True)),
                ("dhis2_external_access", models.BooleanField()),
                ("dhis2_favorite", models.BooleanField()),
                ("dhis2_created", models.DateTimeField()),
                ("dhis2_last_updated", models.DateTimeField()),
                ("dhis2_number", models.BooleanField()),
                ("dhis2_factor", models.IntegerField()),
                (
                    "datasource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalog.datasource",
                    ),
                ),
            ],
            options={
                "ordering": ["dhis2_name"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Dhis2Indicator",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("external_id", models.CharField(max_length=100, unique=True)),
                ("dhis2_name", models.CharField(max_length=200)),
                ("dhis2_short_name", models.CharField(blank=True, max_length=100)),
                ("dhis2_description", models.TextField(blank=True)),
                ("dhis2_external_access", models.BooleanField()),
                ("dhis2_favorite", models.BooleanField()),
                ("dhis2_created", models.DateTimeField()),
                ("dhis2_last_updated", models.DateTimeField()),
                ("dhis2_code", models.CharField(blank=True, max_length=100)),
                ("dhis2_annualized", models.BooleanField()),
                (
                    "datasource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalog.datasource",
                    ),
                ),
                (
                    "dhis2_indicator_type",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="dhis2connector.dhis2indicatortype",
                    ),
                ),
            ],
            options={
                "ordering": ["dhis2_name"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Dhis2DataElement",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("external_id", models.CharField(max_length=100, unique=True)),
                ("dhis2_name", models.CharField(max_length=200)),
                ("dhis2_short_name", models.CharField(blank=True, max_length=100)),
                ("dhis2_description", models.TextField(blank=True)),
                ("dhis2_external_access", models.BooleanField()),
                ("dhis2_favorite", models.BooleanField()),
                ("dhis2_created", models.DateTimeField()),
                ("dhis2_last_updated", models.DateTimeField()),
                ("dhis2_code", models.CharField(blank=True, max_length=100)),
                (
                    "dhis2_domain_type",
                    models.CharField(
                        choices=[("AGGREGATE", "Aggregate"), ("TRACKER", "Tracker")],
                        max_length=100,
                    ),
                ),
                (
                    "dhis2_value_type",
                    models.CharField(
                        choices=[
                            ("TEXT", "Text"),
                            ("LONG_TEXT", "Long text"),
                            ("LETTER", "Letter"),
                            ("PHONE_NUMBER", "Phone number"),
                            ("EMAIL", "Email"),
                            ("YES_NO", "Yes/No"),
                            ("YES_ONLY", "Yes Only"),
                            ("DATE", "Date"),
                            ("DATE_AND_TIME", "Date & Time"),
                            ("TIME", "Time"),
                            ("NUMBER", "Number"),
                            ("UNIT_INTERVAL", "Unit interval"),
                            ("PERCENTAGE", "Percentage"),
                            ("INTEGER", "Integer"),
                            ("INTEGER_POSITIVE", "Positive Integer"),
                            ("INTEGER_NEGATIVE", "Negative Integer"),
                            ("INTEGER_ZERO_OR_POSITIVE", "Positive or Zero Integer"),
                            ("TRACKER_ASSOCIATE", "Tracker Associate"),
                            ("USERNAME", "Username"),
                            ("COORDINATE", "Coordinate"),
                            ("ORGANISATION_UNIT", "Organisation Unit"),
                            ("AGE", "Age"),
                            ("URL", "URL"),
                            ("FILE", "File"),
                            ("IMAGE", "Image"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "dhis2_aggregation_type",
                    models.CharField(
                        choices=[
                            ("AVERAGE", "Average"),
                            ("AVERAGE_SUM_ORG_UNIT ", "Average sum for org unit"),
                            ("COUNT", "Count"),
                            ("CUSTOM", "Custom"),
                            ("DEFAULT", "Default"),
                            ("LAST", "Last"),
                            ("LAST_AVERAGE_ORG_UNIT", "Last average for org unit"),
                            ("MAX", "Max"),
                            ("MIN", "Min"),
                            ("NONE", "None"),
                            ("STDDEV", "Standard Deviation"),
                            ("SUM", "Sum"),
                            ("VARIANCE", "Variance"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "datasource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="catalog.datasource",
                    ),
                ),
            ],
            options={
                "ordering": ["dhis2_name"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Dhis2Connector",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("api_url", models.URLField()),
                ("api_username", models.CharField(max_length=200)),
                ("api_password", models.CharField(max_length=200)),
                (
                    "preferred_locale",
                    habari.common.models.LocaleField(
                        choices=[
                            ("af", "Afrikaans"),
                            ("sq", "Albanian"),
                            ("ar-dz", "Algerian Arabic"),
                            ("ar", "Arabic"),
                            ("es-ar", "Argentinian Spanish"),
                            ("hy", "Armenian"),
                            ("ast", "Asturian"),
                            ("en-au", "Australian English"),
                            ("az", "Azerbaijani"),
                            ("eu", "Basque"),
                            ("be", "Belarusian"),
                            ("bn", "Bengali"),
                            ("bs", "Bosnian"),
                            ("pt-br", "Brazilian Portuguese"),
                            ("br", "Breton"),
                            ("en-gb", "British English"),
                            ("bg", "Bulgarian"),
                            ("my", "Burmese"),
                            ("ca", "Catalan"),
                            ("es-co", "Colombian Spanish"),
                            ("hr", "Croatian"),
                            ("cs", "Czech"),
                            ("da", "Danish"),
                            ("nl", "Dutch"),
                            ("en", "English"),
                            ("eo", "Esperanto"),
                            ("et", "Estonian"),
                            ("fi", "Finnish"),
                            ("fr", "French"),
                            ("fy", "Frisian"),
                            ("gl", "Galician"),
                            ("ka", "Georgian"),
                            ("de", "German"),
                            ("el", "Greek"),
                            ("he", "Hebrew"),
                            ("hi", "Hindi"),
                            ("hu", "Hungarian"),
                            ("is", "Icelandic"),
                            ("io", "Ido"),
                            ("ig", "Igbo"),
                            ("id", "Indonesian"),
                            ("ia", "Interlingua"),
                            ("ga", "Irish"),
                            ("it", "Italian"),
                            ("ja", "Japanese"),
                            ("kab", "Kabyle"),
                            ("kn", "Kannada"),
                            ("kk", "Kazakh"),
                            ("km", "Khmer"),
                            ("ko", "Korean"),
                            ("ky", "Kyrgyz"),
                            ("lv", "Latvian"),
                            ("lt", "Lithuanian"),
                            ("dsb", "Lower Sorbian"),
                            ("lb", "Luxembourgish"),
                            ("mk", "Macedonian"),
                            ("ml", "Malayalam"),
                            ("mr", "Marathi"),
                            ("es-mx", "Mexican Spanish"),
                            ("mn", "Mongolian"),
                            ("ne", "Nepali"),
                            ("es-ni", "Nicaraguan Spanish"),
                            ("no", "Norwegian"),
                            ("nb", "Norwegian Bokmal"),
                            ("nn", "Norwegian Nynorsk"),
                            ("os", "Ossetic"),
                            ("fa", "Persian"),
                            ("pl", "Polish"),
                            ("pt", "Portuguese"),
                            ("pa", "Punjabi"),
                            ("ro", "Romanian"),
                            ("ru", "Russian"),
                            ("gd", "Scottish Gaelic"),
                            ("sr", "Serbian"),
                            ("sr-latn", "Serbian Latin"),
                            ("zh-hans", "Simplified Chinese"),
                            ("sk", "Slovak"),
                            ("sl", "Slovenian"),
                            ("es", "Spanish"),
                            ("sw", "Swahili"),
                            ("sv", "Swedish"),
                            ("tg", "Tajik"),
                            ("ta", "Tamil"),
                            ("tt", "Tatar"),
                            ("te", "Telugu"),
                            ("th", "Thai"),
                            ("zh-hant", "Traditional Chinese"),
                            ("tr", "Turkish"),
                            ("tk", "Turkmen"),
                            ("udm", "Udmurt"),
                            ("uk", "Ukrainian"),
                            ("hsb", "Upper Sorbian"),
                            ("ur", "Urdu"),
                            ("uz", "Uzbek"),
                            ("es-ve", "Venezuelan Spanish"),
                            ("vi", "Vietnamese"),
                            ("cy", "Welsh"),
                        ],
                        default="en",
                        max_length=7,
                    ),
                ),
                (
                    "datasource",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="connector",
                        to="catalog.datasource",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
