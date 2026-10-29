from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from rest_framework import status

from apps.core.models import PublishStatus
from apps.core.validators import (
    validate_no_banned_phrases, validate_no_placeholders, validate_secure_file_upload
)
from apps.entities.models import (
    Group, Company, Brand, Platform, Foundation, Relationship, RelationshipType, MarketScope
)
from apps.taxonomy.models import Capability, Market, MarketStatus
from apps.people.models import Person, PersonGroup
from apps.enquiries.models import EnquiryRoute, Enquiry

class ContentGovernanceTests(TestCase):
    def test_banned_phrase_validator(self):
        # Promotional superlatives must be blocked
        with self.assertRaises(ValidationError):
            validate_no_banned_phrases("We are the leading provider of fine diamonds.")
        with self.assertRaises(ValidationError):
            validate_no_banned_phrases("World-class manufacturing infrastructure.")
        with self.assertRaises(ValidationError):
            validate_no_banned_phrases("Our revolutionary technology platform.")

    def test_placeholder_validator(self):
        with self.assertRaises(ValidationError):
            validate_no_placeholders("Revenue details: TBD")
        with self.assertRaises(ValidationError):
            validate_no_placeholders("TODO: insert client logo here")
        with self.assertRaises(ValidationError):
            validate_no_placeholders("Lorem ipsum dolor sit amet")

    def test_benavi_must_be_india_only(self):
        brand = Brand(
            name="BENAVI",
            slug="benavi",
            category="Fine Silver Jewellery",
            market_scope=MarketScope.INTERNATIONAL, # Prohibited per canonical rules!
            status=PublishStatus.DRAFT,
        )
        with self.assertRaises(ValidationError):
            brand.clean()

    def test_skad_cannot_be_called_holding_company(self):
        group = Group(
            name="SKAD Holding Company",
            slug="skad-holding",
            status=PublishStatus.DRAFT,
        )
        with self.assertRaises(ValidationError):
            group.clean()

    def test_market_requires_evidence_note(self):
        market = Market(
            region="North America",
            country="US",
            status=MarketStatus.ACTIVE,
            evidence_note="", # Missing mandatory private documentation
        )
        with self.assertRaises(ValidationError):
            market.clean()

    def test_person_requires_recorded_consent_to_publish(self):
        person = Person(
            name="Alex Sterling",
            slug="alex-sterling",
            title="Chief Technology Officer",
            group=PersonGroup.LEADERSHIP,
            bio="Seasoned software architect.",
            status=PublishStatus.PUBLISHED,
            consent_recorded=False, # Must have consent to publish
        )
        with self.assertRaises(ValidationError):
            person.clean()

class RelationshipConstraintTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="SKAD Jewels India",
            slug="skad-jewels",
            legal_name="SKAD JEWELS INDIA PRIVATE LIMITED",
            company_type="Manufacturing + Diamond Trading",
            sector="Jewellery & Diamonds",
            status=PublishStatus.DRAFT,
        )
        self.brand = Brand.objects.create(
            name="BENAVI",
            slug="benavi",
            category="Fine Silver Jewellery",
            market_scope=MarketScope.INDIA_ONLY,
            status=PublishStatus.DRAFT,
        )
        self.platform = Platform.objects.create(
            name="SKAD CommerceOS",
            slug="skad-commerceos",
            tagline="BUILD • LAUNCH • GROW",
            status="Active",
        )
        self.foundation = Foundation.objects.create(
            name="Kalla Rudra Foundation",
            slug="kalla-rudra-foundation",
            status=PublishStatus.DRAFT,
        )

    def test_brand_cannot_own_company(self):
        brand_ct = ContentType.objects.get_for_model(Brand)
        company_ct = ContentType.objects.get_for_model(Company)
        rel = Relationship(
            from_type=brand_ct,
            from_id=self.brand.id,
            to_type=company_ct,
            to_id=self.company.id,
            relationship=RelationshipType.OWNS_BRAND,
        )
        with self.assertRaises(ValidationError):
            rel.clean()

    def test_platform_cannot_own_brand(self):
        plat_ct = ContentType.objects.get_for_model(Platform)
        brand_ct = ContentType.objects.get_for_model(Brand)
        rel = Relationship(
            from_type=plat_ct,
            from_id=self.platform.id,
            to_type=brand_ct,
            to_id=self.brand.id,
            relationship=RelationshipType.OWNS_BRAND,
        )
        with self.assertRaises(ValidationError):
            rel.clean()

    def test_foundation_cannot_own_commercial_brand(self):
        found_ct = ContentType.objects.get_for_model(Foundation)
        brand_ct = ContentType.objects.get_for_model(Brand)
        rel = Relationship(
            from_type=found_ct,
            from_id=self.foundation.id,
            to_type=brand_ct,
            to_id=self.brand.id,
            relationship=RelationshipType.OPERATES,
        )
        with self.assertRaises(ValidationError):
            rel.clean()

class SecurityAndFileUploadTests(TestCase):
    def test_dangerous_extension_rejected(self):
        malicious_file = SimpleUploadedFile("malware.exe", b"malicious binary content", content_type="application/octet-stream")
        with self.assertRaises(ValidationError):
            validate_secure_file_upload(malicious_file)

    def test_oversized_file_rejected(self):
        # 11MB file with 10MB limit
        big_content = b"0" * (11 * 1024 * 1024)
        big_file = SimpleUploadedFile("report.pdf", big_content, content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_secure_file_upload(big_file, max_mb=10)

    def test_valid_pdf_accepted(self):
        valid_pdf = SimpleUploadedFile("whitepaper.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        # Should execute cleanly without raising ValidationError
        validate_secure_file_upload(valid_pdf, max_mb=10)

class ApiEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.route = EnquiryRoute.objects.create(
            code="technology",
            label="Technology & Platforms",
            to_emails=["tech@skadgroup.com"],
            active=True,
        )

    def test_health_check(self):
        response = self.client.get("/api/v1/health/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "online")
        self.assertEqual(response.data["philosophy"], "BUILD • CONNECT • SCALE")

    def test_navigation_endpoint(self):
        response = self.client.get("/api/v1/navigation/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("primary_nav", response.data)
        self.assertIn("primary_cta", response.data)

    def test_ecosystem_endpoint(self):
        response = self.client.get("/api/v1/ecosystem/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("nodes", response.data)
        self.assertIn("accessible_list", response.data)

    def test_enquiry_submission_success(self):
        payload = {
            "route_code": "technology",
            "name": "Jane Doe",
            "company": "Global Tech Corp",
            "email": "jane@example.com",
            "country": "GB",
            "message": "Interested in CommerceOS API integration.",
        }
        response = self.client.post("/api/v1/enquiries/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("reference", response.data)
        self.assertTrue(response.data["reference"].startswith("SKD-"))

    def test_enquiry_honeypot_rejection(self):
        payload = {
            "route_code": "technology",
            "name": "Bot Submitter",
            "email": "bot@example.com",
            "country": "US",
            "message": "Spam message",
            "website": "http://spamsite.com", # Honeypot triggered
        }
        response = self.client.post("/api/v1/enquiries/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_redirect_signal_on_slug_change(self):
        from apps.entities.models import Company
        from apps.seo.models import Redirect
        comp = Company.objects.create(
            name="Test Jewels",
            slug="test-jewels-old",
            legal_name="TEST JEWELS LTD",
            company_type="Manufacturing",
            sector="Jewellery",
            status=PublishStatus.PUBLISHED,
            verified=True,
        )
        # Update slug
        comp.slug = "test-jewels-new"
        comp.save()

        # Check that 301 Redirect was auto-created
        redirect = Redirect.objects.filter(old_path="/companies/test-jewels-old").first()
        self.assertIsNotNone(redirect)
        self.assertEqual(redirect.new_path, "/companies/test-jewels-new")
        self.assertTrue(redirect.permanent)

    def test_group_endpoint(self):
        response = self.client.get("/api/v1/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_press_releases_and_case_studies_endpoints(self):
        resp_pr = self.client.get("/api/v1/press-releases/")
        self.assertEqual(resp_pr.status_code, status.HTTP_200_OK)

        resp_cs = self.client.get("/api/v1/case-studies/")
        self.assertEqual(resp_cs.status_code, status.HTTP_200_OK)

        resp_rep = self.client.get("/api/v1/reports/")
        self.assertEqual(resp_rep.status_code, status.HTTP_200_OK)

        resp_ev = self.client.get("/api/v1/events/")
        self.assertEqual(resp_ev.status_code, status.HTTP_200_OK)

    def test_subscription_confirm_flow(self):
        from apps.enquiries.models import Subscription
        sub = Subscription.objects.create(email="reader@example.com", opt_in_token="test-token-12345")
        
        # Confirm subscription with token
        confirm_resp = self.client.get("/api/v1/subscriptions/confirm/?token=test-token-12345")
        self.assertEqual(confirm_resp.status_code, status.HTTP_200_OK)
        
        sub.refresh_from_db()
        self.assertTrue(sub.confirmed)

    def test_structured_data_endpoint(self):
        resp = self.client.get("/api/v1/seo/structured-data/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["@type"], "Corporation")
        self.assertIn("subOrganization", resp.data)

    def test_feature_flags_endpoint(self):
        from apps.content.models import FeatureFlag
        FeatureFlag.objects.create(key="test_flag", label="Test Flag", enabled=True)
        resp = self.client.get("/api/v1/feature-flags/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get("test_flag"))
        self.assertIn("markets_map", resp.data)
        self.assertIn("investment_route", resp.data)

    def test_theme_tokens_endpoint(self):
        from apps.content.models import ThemeToken
        ThemeToken.objects.create(key="palette.custom_gold", value="#FFD700", group="palette")
        resp = self.client.get("/api/v1/theme/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("palette", resp.data)
        self.assertEqual(resp.data["palette"]["custom_gold"], "#FFD700")
        self.assertEqual(resp.data["palette"]["primary_navy"], "#0A1F44")

    def test_industry_platform_and_foundation_relations(self):
        from apps.taxonomy.models import Industry
        from apps.entities.models import Platform, Foundation
        ind = Industry.objects.create(
            name="Commerce & Tech", slug="commerce-tech-test",
            status=PublishStatus.PUBLISHED, verified=True
        )
        plat = Platform.objects.create(
            name="CommerceOS Test", slug="commerceos-test",
            status=PublishStatus.PUBLISHED, verified=True
        )
        found = Foundation.objects.create(
            name="Impact Test", slug="impact-test",
            status=PublishStatus.PUBLISHED, verified=True
        )
        plat.industries.add(ind)
        found.industries.add(ind)

        resp = self.client.get(f"/api/v1/industries/{ind.slug}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("CommerceOS Test", resp.data["platforms"])
        self.assertIn("Impact Test", resp.data["foundations"])

    def test_section_content_pydantic_validation(self):
        from apps.content.models import Page, Section
        from django.core.exceptions import ValidationError

        page = Page.objects.create(
            title="Home Page Test", slug="home-test-pydantic",
            status=PublishStatus.PUBLISHED, verified=True
        )

        # Insecure external URL should fail validation per Doc 2 Page 15
        invalid_section = Section(
            page=page,
            type="hero",
            order=1,
            content={
                "headline_lines": ["BUILDING BUSINESSES."],
                "supporting_copy": "Valid copy for testing hero block.",
                "primary_cta": {
                    "label": "VISIT",
                    "kind": "external",
                    "target": "http://insecure-site.com" # Prohibited! Must be https
                }
            }
        )
        with self.assertRaises(ValidationError):
            invalid_section.clean()

        # Secure external URL should pass validation
        valid_section = Section(
            page=page,
            type="hero",
            order=1,
            content={
                "headline_lines": ["BUILDING BUSINESSES."],
                "supporting_copy": "Valid copy for testing hero block.",
                "primary_cta": {
                    "label": "VISIT",
                    "kind": "external",
                    "target": "https://secure-site.com"
                }
            }
        )
        valid_section.clean()

    def test_preview_token_generation_and_validation(self):
        from apps.core.utils import generate_preview_token, validate_preview_token
        token = generate_preview_token("company", "skad-jewels")
        self.assertTrue(validate_preview_token(token, "company", "skad-jewels"))
        self.assertFalse(validate_preview_token(token, "company", "wrong-slug"))
        self.assertFalse(validate_preview_token("invalid-tampered-token", "company", "skad-jewels"))

    def test_magic_bytes_file_validation(self):
        # A file with .pdf extension but binary junk without %PDF header must fail
        fake_pdf = SimpleUploadedFile("fake.pdf", b"MZ_THIS_IS_AN_EXE_NOT_A_PDF", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            validate_secure_file_upload(fake_pdf, max_mb=10)

    def test_admin_deletion_guard_blocks_without_redirect(self):
        from apps.core.admin import PublishableAdmin
        from apps.entities.models import Company
        from apps.entities.admin import CompanyAdmin
        from apps.seo.models import Redirect
        from django.contrib.admin.sites import AdminSite

        site = AdminSite()
        admin_instance = CompanyAdmin(Company, site)

        published_comp = Company.objects.create(
            name="Guarded Company",
            slug="guarded-comp",
            legal_name="GUARDED COMPANY LTD",
            company_type="Manufacturing",
            sector="Jewellery",
            status=PublishStatus.PUBLISHED,
            verified=True,
            noindex=False,
        )

        # Deleting without an active redirect must raise ValidationError
        with self.assertRaises(ValidationError):
            admin_instance._check_deletion_guard(published_comp)

        # Once a 301 Redirect exists, deletion guard passes
        Redirect.objects.create(old_path="/companies/guarded-comp", new_path="/companies/new-comp")
        admin_instance._check_deletion_guard(published_comp) # Should not raise

    def test_seeded_content_structure(self):
        from django.core.management import call_command
        from apps.content.models import Page, Section, UIString, NavigationItem, FooterColumn, SiteSettings
        from apps.entities.models import Group, Company, Brand, Platform
        from apps.enquiries.models import EnquiryRoute

        # Execute seed command on the test database
        call_command("seed_skad")

        # Check Page and Section
        home_page = Page.objects.filter(slug="home").first()
        self.assertIsNotNone(home_page)

        self.assertTrue(home_page.sections.filter(type="hero").exists())
        self.assertTrue(home_page.sections.filter(type="ecosystem").exists())

        # Check UIStrings
        self.assertTrue(UIString.objects.filter(key="cta.partner_with_skad").exists())
        self.assertTrue(UIString.objects.filter(key="form.error.email_invalid").exists())

        # Check Navigation Items
        self.assertTrue(NavigationItem.objects.filter(label="COMPANIES").exists())
        self.assertTrue(NavigationItem.objects.filter(label="BRANDS").exists())

        # Check Footer Columns
        self.assertTrue(FooterColumn.objects.filter(title="GROUP").exists())

        # Check Site Settings
        settings_obj = SiteSettings.objects.first()
        self.assertIsNotNone(settings_obj)
        self.assertEqual(settings_obj.group_name, "SKAD GROUP")
        self.assertEqual(settings_obj.operating_philosophy, "BUILD • CONNECT • SCALE")

        # Check Enquiry Routes (11 canonical routes)
        self.assertEqual(EnquiryRoute.objects.count(), 11)
        self.assertFalse(EnquiryRoute.objects.get(code="investment").active)

    def test_draft_content_blocked_without_preview_token(self):
        from apps.content.models import Article
        from apps.taxonomy.models import Category
        category = Category.objects.create(name="Tech", slug="tech-cat")
        draft_article = Article.objects.create(
            title="Secret Draft Article",
            slug="secret-draft",
            category=category,
            body="Confidential internal draft content",
            status=PublishStatus.DRAFT,
            verified=False,
        )

        # Insecure ?preview=true query must NOT leak the draft to anonymous clients
        resp = self.client.get("/api/v1/articles/?preview=true")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        slugs = [item["slug"] for item in resp.data.get("results", [])]
        self.assertNotIn("secret-draft", slugs)

    def test_draft_content_accessible_with_valid_preview_token(self):
        from apps.content.models import Article
        from apps.taxonomy.models import Category
        from apps.core.utils import generate_preview_token
        category = Category.objects.create(name="Tech 2", slug="tech-cat-2")
        draft_article = Article.objects.create(
            title="Previewable Draft Article",
            slug="preview-draft",
            category=category,
            body="Previewable draft content",
            status=PublishStatus.DRAFT,
            verified=False,
        )

        valid_token = generate_preview_token("article", "preview-draft")
        resp = self.client.get(f"/api/v1/articles/?preview_token={valid_token}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        slugs = [item["slug"] for item in resp.data.get("results", [])]
        self.assertIn("preview-draft", slugs)

    def test_document_download_blocks_unapproved_or_internal(self):
        from apps.documents.models import Document, DocumentVersion
        from django.core.files.uploadedfile import SimpleUploadedFile
        doc = Document.objects.create(
            title="Internal Secret Audit",
            slug="internal-secret-audit",
            doc_type="report",
            visibility="internal",
            status=PublishStatus.DRAFT,
            verified=False,
        )
        fake_file = SimpleUploadedFile("audit.pdf", b"%PDF-1.4 internal report", content_type="application/pdf")
        version = DocumentVersion.objects.create(
            document=doc,
            file=fake_file,
            version_label="v1.0",
            issued_on="2026-10-01",
        )
        doc.current_version = version
        doc.save()

        # Downloading internal/unapproved document must return 404
        resp = self.client.get(f"/api/v1/documents/{doc.id}/download/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_opportunity_honeypot_rejection(self):
        payload = {
            "opportunity_type": "strategic_partnership",
            "name": "Spam Bot",
            "email": "bot@spammer.com",
            "summary": "Buy cheap traffic",
            "website": "http://spambot-link.com", # Honeypot triggered
        }
        resp = self.client.post("/api/v1/opportunities/", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prune_expired_applications(self):
        from apps.careers.models import Application
        from apps.careers.tasks import prune_expired_applications
        from django.utils import timezone
        import datetime

        yesterday = timezone.now().date() - datetime.timedelta(days=1)
        expired_app = Application.objects.create(
            candidate_name="Expired Candidate",
            email="expired@example.com",
            retention_date=yesterday,
            consent_recorded=True,
        )

        tomorrow = timezone.now().date() + datetime.timedelta(days=30)
        active_app = Application.objects.create(
            candidate_name="Active Candidate",
            email="active@example.com",
            retention_date=tomorrow,
            consent_recorded=True,
        )

        prune_expired_applications()

        self.assertFalse(Application.objects.filter(id=expired_app.id).exists())
        self.assertTrue(Application.objects.filter(id=active_app.id).exists())

    def test_revalidation_replay_protection(self):
        import time
        import hmac
        import hashlib
        from django.conf import settings

        old_timestamp = str(time.time() - 600)  # 10 minutes ago (replay attack)
        payload = b'{"tags": ["sitemap"]}'
        sig = hmac.new(settings.REVALIDATE_SECRET.encode(), payload, hashlib.sha256).hexdigest()

        resp = self.client.post(
            "/api/v1/internal/revalidate-hook/",
            data=payload,
            content_type="application/json",
            HTTP_X_SKAD_SIGNATURE=sig,
            HTTP_X_SKAD_TIMESTAMP=old_timestamp,
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_csp_header(self):
        resp = self.client.get("/admin/login/")
        self.assertIn("Content-Security-Policy", resp.headers)
