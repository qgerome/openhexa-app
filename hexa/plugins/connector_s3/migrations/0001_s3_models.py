# Generated by Django 3.1.7 on 2021-04-01 15:58

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import hexa.common.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user_management", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Bucket",
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
                ("name", models.CharField(max_length=200)),
                ("short_name", models.CharField(blank=True, max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "countries",
                    django_countries.fields.CountryField(
                        blank=True, max_length=746, multiple=True
                    ),
                ),
                ("url", models.URLField(blank=True)),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("active_from", models.DateTimeField(blank=True, null=True)),
                ("active_to", models.DateTimeField(blank=True, null=True)),
                (
                    "public",
                    models.BooleanField(default=False, verbose_name="Public dataset"),
                ),
                (
                    "locale",
                    hexa.common.models.LocaleField(
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
                ("s3_name", models.CharField(max_length=200)),
                ("s3_access_key_id", models.CharField(max_length=200)),
                ("s3_secret_access_key", models.CharField(max_length=200)),
                (
                    "owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="user_management.organization",
                    ),
                ),
            ],
            options={
                "verbose_name": "S3 Bucket",
                "ordering": ("name",),
            },
        ),
    ]
