from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

from apps.core.models import PublishStatus
from apps.entities.models import (
    Group, Company, Brand, Platform, Venture, Foundation,
    Relationship, RelationshipType, MarketScope
)
from django.contrib.auth.models import Group as AuthGroup
from apps.taxonomy.models import Industry, Capability
from apps.enquiries.models import EnquiryRoute
from apps.content.models import (
    ThemeToken, FeatureFlag, UIString, SiteSettings,
    NavigationItem, FooterColumn, Page, Section
)


class Command(BaseCommand):
    help = "Seeds initial canonical SKAD GROUP structure per the specification (idempotent, draft/unverified)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding canonical SKAD GROUP ecosystem..."))

        # 1. Seed 10 Industries
        industries_data = [
            ("Jewellery & Diamonds", "Fine diamond, silver, and precious gemstone ecosystems."),
            ("Manufacturing", "Precision jewellery and multi-sector manufacturing infrastructure."),
            ("International Trade", "Global cross-border commerce, import, export, and supply chain logistics."),
            ("Beauty & Personal Care", "Comprehensive beauty, hair, skin, and wellness studio services."),
            ("Fashion & Lifestyle", "Contemporary apparel, cultural heritage sarees, and modern streetwear."),
            ("Legal Technology", "Next-generation legal automation, intelligence, and accessibility tools."),
            ("Commerce Technology", "Digital commerce infrastructure, platforms, and intelligence systems."),
            ("AI & Automation", "AI-assisted workflows, analytics, and intelligent operations."),
            ("Social Impact", "Community upliftment, foundation initiatives, and social welfare programs."),
            ("Strategic Ventures", "Incubation of emerging brands and high-potential market opportunities."),
        ]
        industries_map = {}
        for name, desc in industries_data:
            slug = slugify(name)
            ind, created = Industry.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": desc,
                    "status": PublishStatus.DRAFT,
                    "verified": False,
                },
            )
            industries_map[slug] = ind

        # 2. Seed 17 Capabilities
        capabilities_data = [
            ("Strategy", "Brand & Growth", "High-level market positioning and commercial strategic architecture."),
            ("Market Intelligence", "Research & Analytics", "Data-driven category research and market demand forecasting."),
            ("Manufacturing", "Production & Supply", "Verified precision manufacturing and quality production."),
            ("Diamond Trading", "Trade & Sourcing", "Global sourcing and B2B trade of natural and lab-grown diamonds."),
            ("International Trade", "Trade & Sourcing", "Cross-border export, import, compliance, and customs infrastructure."),
            ("Product Development", "Product & Design", "End-to-end product ideation, prototyping, and material sourcing."),
            ("Brand Building", "Brand & Creative", "Distinctive visual identity, narrative development, and positioning."),
            ("Technology", "Digital & Engineering", "Modern full-stack web platforms, mobile architecture, and systems."),
            ("AI", "Intelligence & Automation", "Practical artificial intelligence integration and automated workflows."),
            ("E-commerce", "Commerce & Sales", "Scalable digital storefronts, marketplace integrations, and checkout optimization."),
            ("Commerce", "Commerce & Sales", "Omnichannel distribution and direct-to-consumer operational workflows."),
            ("Marketing", "Growth & Acquisition", "Omnichannel performance marketing and brand awareness campaigns."),
            ("SEO", "Search & Discovery", "Organic search optimization, technical search readiness, and structured data."),
            ("GEO", "Search & Discovery", "Generative Engine Optimization for AI-driven conversational discovery."),
            ("CRM", "Retention & Operations", "Customer lifecycle management, personalization, and retention systems."),
            ("Automation", "Intelligence & Automation", "Workflow automation and business process optimization."),
            ("Operations", "Enterprise Infrastructure", "Repeatable operational playbooks and scalable corporate processes."),
        ]
        capabilities_map = {}
        for name, group, desc in capabilities_data:
            slug = slugify(name)
            cap, created = Capability.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "group": group,
                    "description": desc,
                    "status": PublishStatus.DRAFT,
                    "verified": False,
                },
            )
            capabilities_map[slug] = cap

        # 2b. Seed SKAD GROUP (Canonical Group Ecosystem Entity)
        Group.objects.get_or_create(
            slug="skad-group",
            defaults={
                "name": "SKAD GROUP",
                "primary_line": "BUILDING BUSINESSES. CREATING BRANDS. SHAPING THE FUTURE.",
                "operating_philosophy": "BUILD • CONNECT • SCALE",
                "summary": "Diversified corporate ecosystem building companies, brands, platforms, and ventures.",
                "status": PublishStatus.DRAFT,
                "verified": False,
            },
        )

        # 3. Seed Companies
        companies_data = [
            {
                "name": "SKAD Jewels India",
                "slug": "skad-jewels",
                "legal_name": "SKAD JEWELS INDIA PRIVATE LIMITED",
                "company_type": "Manufacturing + Diamond Trading",
                "sector": "Jewellery & Diamonds",
                "city": "Surat",
                "country": "IN",
                "summary": "Manufacturing, sourcing, B2B supply, and international commerce in natural and lab-grown diamonds.",
            },
            {
                "name": "Luxora Glow Essentials",
                "slug": "luxora-glow-essentials",
                "legal_name": "LUXORA GLOW ESSENTIALS PRIVATE LIMITED",
                "company_type": "Beauty + Personal Care",
                "sector": "Beauty & Personal Care",
                "city": "Mumbai",
                "country": "IN",
                "summary": "Professional hair, skin, and personal care studio ecosystem.",
            },
            {
                "name": "Detara Ltd",
                "slug": "detara-ltd",
                "legal_name": "DETARA LTD",
                "company_type": "Fine Jewellery Company",
                "sector": "Jewellery & Diamonds",
                "city": "London",
                "country": "GB",
                "summary": "UK corporate entity operating premium fine diamond jewellery.",
            },
            {
                "name": "SKAD Diatech Exports",
                "slug": "skad-diatech-exports",
                "legal_name": "SKAD DIATECH EXPORTS",
                "company_type": "International Trade + Commerce Infrastructure",
                "sector": "International Trade",
                "city": "Surat",
                "country": "IN",
                "summary": "International trade ecosystem housing CommerceOS and Commerce Lab platforms.",
            },
        ]
        companies_map = {}
        for cdata in companies_data:
            comp, created = Company.objects.get_or_create(
                slug=cdata["slug"],
                defaults={
                    "name": cdata["name"],
                    "legal_name": cdata["legal_name"],
                    "company_type": cdata["company_type"],
                    "sector": cdata["sector"],
                    "city": cdata.get("city", ""),
                    "country": cdata.get("country", ""),
                    "summary": cdata["summary"],
                    "status": PublishStatus.DRAFT,
                    "verified": False,
                },
            )
            companies_map[cdata["slug"]] = comp

        # 4. Seed Brands
        brands_data = [
            {
                "name": "DETARA",
                "slug": "detara",
                "category": "Fine Diamond Jewellery & Engagement Rings",
                "market_scope": MarketScope.INTERNATIONAL,
                "tagline": "Fine Diamond Jewellery & Engagement Rings",
                "cta_label": "EXPLORE DETARA",
                "summary": "Premium diamond jewellery and bridal collections crafted with ethical standards.",
            },
            {
                "name": "LUXORA GLOW",
                "slug": "luxora-glow",
                "category": "Hair, Skin & Beauty Studio",
                "market_scope": MarketScope.REGIONAL,
                "tagline": "Hair, Skin & Beauty Studio",
                "cta_label": "EXPLORE LUXORA GLOW",
                "summary": "Boutique beauty studio offering verified personalized hair and skincare services.",
            },
            {
                "name": "BENAVI",
                "slug": "benavi",
                "category": "Fine Silver Jewellery",
                "market_scope": MarketScope.INDIA_ONLY,
                "tagline": "Crafting Dreams in Silver: Your Story, Your Jewel.",
                "cta_label": "VISIT BENAVI",
                "summary": "India-only contemporary silver jewellery, personalized designs, and custom craft.",
            },
            {
                "name": "RUPAARI",
                "slug": "rupaari",
                "category": "Fashion / Sarees / Indian Heritage",
                "market_scope": MarketScope.REGIONAL,
                "tagline": "Heritage textiles and Indian ethnic elegance",
                "cta_label": "EXPLORE RUPAARI",
                "summary": "Celebration of traditional Indian weaves, authentic artisanal sarees, and heritage wear.",
            },
            {
                "name": "CASE SUNO",
                "slug": "case-suno",
                "category": "Legal Technology",
                "market_scope": MarketScope.REGIONAL,
                "tagline": "Legal Intelligence & Advisory Technology",
                "cta_label": "EXPLORE CASE SUNO",
                "summary": "Modern legal tech making legal accessibility and case documentation intuitive.",
            },
            {
                "name": "ZEMO",
                "slug": "zemo",
                "category": "New-Gen Fashion & Custom Wear",
                "market_scope": MarketScope.REGIONAL,
                "tagline": "CUSTOM • STREETWEAR • INNERWEAR - WEAR YOUR WAY.",
                "cta_label": "CREATE YOUR ZEMO",
                "summary": "Expressive new-generation streetwear and custom-fit apparel for urban creators.",
            },
        ]
        brands_map = {}
        for bdata in brands_data:
            br, created = Brand.objects.get_or_create(
                slug=bdata["slug"],
                defaults={
                    "name": bdata["name"],
                    "category": bdata["category"],
                    "market_scope": bdata["market_scope"],
                    "tagline": bdata["tagline"],
                    "cta_label": bdata["cta_label"],
                    "summary": bdata["summary"],
                    "status": PublishStatus.DRAFT,
                    "verified": False,
                },
            )
            brands_map[bdata["slug"]] = br

        # 5. Seed Platforms
        platforms_data = [
            {
                "name": "SKAD COMMERCEOS",
                "slug": "skad-commerceos",
                "tagline": "BUILD • LAUNCH • GROW",
                "status": "Active Infrastructure",
                "summary": "Commerce operating system providing infrastructure across product, intelligence, AI, and operations.",
                "cta_label": "EXPLORE COMMERCEOS",
            },
            {
                "name": "SKAD COMMERCE LAB",
                "slug": "skad-commerce-lab",
                "tagline": "AI + HUMAN EXECUTION",
                "status": "Execution Layer",
                "summary": "Strategic and execution service layer combining AI capabilities and expert human craft.",
                "cta_label": "EXPLORE COMMERCE LAB",
            },
        ]
        platforms_map = {}
        for pdata in platforms_data:
            plat, created = Platform.objects.get_or_create(
                slug=pdata["slug"],
                defaults={
                    "name": pdata["name"],
                    "tagline": pdata["tagline"],
                    "summary": pdata["summary"],
                    "cta_label": pdata["cta_label"],
                    "status": PublishStatus.DRAFT,
                    "verified": False,
                },
            )
            platforms_map[pdata["slug"]] = plat

        # 6. Seed Ventures & Foundation
        Venture.objects.get_or_create(
            slug="future-ventures",
            defaults={
                "name": "FUTURE VENTURES",
                "venture_type": "Strategic Incubation & Opportunities",
                "stage_label": "Active Intake",
                "summary": "Controlled entry point for new business concepts, strategic joint ventures, and partnerships.",
                "status": PublishStatus.DRAFT,
                "verified": False,
            },
        )
        foundation_obj, _ = Foundation.objects.get_or_create(
            slug="kalla-rudra-foundation",
            defaults={
                "name": "KALLA RUDRA FOUNDATION",
                "mission": "Dedicated to educational scholarships, healthcare support, and sustainable community empowerment.",
                "summary": "Social impact arm of the SKAD ecosystem, operating independently from commercial activities.",
                "status": PublishStatus.DRAFT,
                "verified": False,
            },
        )

        # 6b. Wire Industries to Canonical Entities (Doc 1 Page 7 & 13, Doc 2 Page 21)
        if "jewellery-diamonds" in industries_map:
            ind = industries_map["jewellery-diamonds"]
            if "skad-jewels" in companies_map: companies_map["skad-jewels"].industries.add(ind)
            if "detara" in brands_map: brands_map["detara"].industries.add(ind)
            if "benavi" in brands_map: brands_map["benavi"].industries.add(ind)

        if "manufacturing" in industries_map:
            ind = industries_map["manufacturing"]
            if "skad-jewels" in companies_map: companies_map["skad-jewels"].industries.add(ind)

        if "international-trade" in industries_map:
            ind = industries_map["international-trade"]
            if "skad-diatech-exports" in companies_map: companies_map["skad-diatech-exports"].industries.add(ind)

        if "beauty-personal-care" in industries_map:
            ind = industries_map["beauty-personal-care"]
            if "luxora-glow-essentials" in companies_map: companies_map["luxora-glow-essentials"].industries.add(ind)
            if "luxora-glow" in brands_map: brands_map["luxora-glow"].industries.add(ind)

        if "fashion-lifestyle" in industries_map:
            ind = industries_map["fashion-lifestyle"]
            if "rupaari" in brands_map: brands_map["rupaari"].industries.add(ind)
            if "zemo" in brands_map: brands_map["zemo"].industries.add(ind)

        if "legal-technology" in industries_map:
            ind = industries_map["legal-technology"]
            if "case-suno" in brands_map: brands_map["case-suno"].industries.add(ind)

        if "commerce-technology" in industries_map:
            ind = industries_map["commerce-technology"]
            if "skad-commerceos" in platforms_map: platforms_map["skad-commerceos"].industries.add(ind)
            if "skad-commerce-lab" in platforms_map: platforms_map["skad-commerce-lab"].industries.add(ind)

        if "ai-automation" in industries_map:
            ind = industries_map["ai-automation"]
            if "skad-commerce-lab" in platforms_map: platforms_map["skad-commerce-lab"].industries.add(ind)

        if "social-impact" in industries_map:
            ind = industries_map["social-impact"]
            foundation_obj.industries.add(ind)

        # 7. Seed Explicit Entity Relationships (Draft / Unverified per governance)
        company_ct = ContentType.objects.get_for_model(Company)
        brand_ct = ContentType.objects.get_for_model(Brand)
        platform_ct = ContentType.objects.get_for_model(Platform)

        relationships_data = [
            (company_ct, companies_map["skad-jewels"].id, brand_ct, brands_map["benavi"].id, RelationshipType.OPERATES, "SKAD Jewels India operates BENAVI fine silver jewellery brand"),
            (company_ct, companies_map["luxora-glow-essentials"].id, brand_ct, brands_map["luxora-glow"].id, RelationshipType.OPERATES, "Luxora Glow Essentials operates LUXORA GLOW beauty studio"),
            (company_ct, companies_map["detara-ltd"].id, brand_ct, brands_map["detara"].id, RelationshipType.OPERATES, "Detara Ltd operates DETARA UK jewellery brand"),
            (platform_ct, platforms_map["skad-commerceos"].id, company_ct, companies_map["skad-diatech-exports"].id, RelationshipType.SITS_WITHIN, "CommerceOS sits within SKAD Diatech Exports infrastructure"),
            (platform_ct, platforms_map["skad-commerce-lab"].id, company_ct, companies_map["skad-diatech-exports"].id, RelationshipType.SITS_WITHIN, "Commerce Lab sits within SKAD Diatech Exports infrastructure"),
        ]
        for from_t, from_i, to_t, to_i, rel_type, note in relationships_data:
            Relationship.objects.get_or_create(
                from_type=from_t,
                from_id=from_i,
                to_type=to_t,
                to_id=to_i,
                relationship=rel_type,
                defaults={
                    "note": note,
                    "status": PublishStatus.DRAFT,
                    "verified": False,
                },
            )

        # 8. Seed 11 Enquiry Routes
        routes_data = [
            ("general", "General Corporate", ["info@skadgroup.com"], True),
            ("business_partnership", "Business Partnership", ["partners@skadgroup.com"], True),
            ("investment", "Investment / Ventures", ["invest@skadgroup.com"], False), # Inactive until established
            ("supplier", "Supplier & Sourcing", ["sourcing@skadgroup.com"], True),
            ("manufacturing", "Manufacturing", ["manufacturing@skadgroup.com"], True),
            ("diamond_trading", "Diamond Trading", ["diamonds@skadgroup.com"], True),
            ("international_trade", "International Trade", ["trade@skadgroup.com"], True),
            ("technology", "Technology & Platforms", ["tech@skadgroup.com"], True),
            ("media", "Press & Media", ["press@skadgroup.com"], True),
            ("careers", "Careers & Talent", ["careers@skadgroup.com"], True),
            ("foundation", "Foundation & Impact", ["foundation@skadgroup.com"], True),
        ]
        for code, label, emails, is_active in routes_data:
            EnquiryRoute.objects.get_or_create(
                code=code,
                defaults={
                    "label": label,
                    "to_emails": emails,
                    "active": is_active,
                },
            )

        # 9. Seed Canonical Feature Flags (Doc 2 Page 14)
        flags_data = [
            ("markets_map", "Interactive Global Markets Map", True, "Show or hide interactive global market footprint"),
            ("people", "Corporate Leadership & Team", True, "Display leadership and executive team directory"),
            ("newsroom", "Corporate Newsroom & Media", True, "Display press releases and announcements"),
            ("careers", "Careers & Talent Openings", True, "Enable recruitment openings and CV submission"),
            ("search", "Cross-Entity Search", True, "Enable site-wide cross-entity search"),
            ("newsletter", "Newsletter Subscriptions", True, "Enable newsletter double opt-in subscriptions"),
            ("investment_route", "Investment Enquiry Route", False, "Enable when formal investment intake process is active"),
            ("ask_skad", "ASK SKAD AI Assistant", False, "Future conversational intelligence assistant"),
        ]
        for key, label, enabled, desc in flags_data:
            FeatureFlag.objects.get_or_create(
                key=key,
                defaults={
                    "label": label,
                    "enabled": enabled,
                    "description": desc,
                },
            )

        # 10. Seed Approved Design System Theme Tokens (Doc 2 Page 16)
        tokens_data = [
            ("palette.primary_navy", "#0A1F44", "palette", "Primary Navy brand color"),
            ("palette.deep_navy", "#07152F", "palette", "Deep Navy background token"),
            ("palette.champagne_gold", "#D4AF37", "palette", "Champagne Gold accent color"),
            ("palette.metallic_gold", "#B8862D", "palette", "Metallic Gold secondary accent"),
            ("palette.white", "#FFFFFF", "palette", "Pure White surface color"),
            ("palette.warm_off_white", "#F8F7F3", "palette", "Warm Off-White background"),
            ("palette.light_grey", "#F2F3F5", "palette", "Light Grey subtle border/background"),
            ("typography.headline_font", "Cormorant Garamond, serif", "typography", "Editorial headline font"),
            ("typography.body_font", "Plus Jakarta Sans, sans-serif", "typography", "Clean legible body font"),
        ]
        for key, value, group, desc in tokens_data:
            ThemeToken.objects.get_or_create(
                key=key,
                defaults={
                    "value": value,
                    "group": group,
                    "description": desc,
                },
            )

        # 11. Seed Canonical Roles & Permissions Groups (Doc 2 Page 9)
        roles_data = [
            "Superadmin / Developer",
            "Approver",
            "Editor",
            "Brand / company owner",
            "HR",
            "Enquiry handler",
            "Media",
            "Read-only / auditor",
        ]
        for role_name in roles_data:
            AuthGroup.objects.get_or_create(name=role_name)

        # 12. Seed UIStrings (Microcopy & Button Labels per Doc 1 Page 15 & Doc 2 Page 16)
        ui_strings_data = [
            ("cta.partner_with_skad", "PARTNER WITH SKAD", "Primary corporate call-to-action"),
            ("cta.explore_the_group", "EXPLORE THE GROUP", "Hero section primary link"),
            ("cta.explore_detara", "EXPLORE DETARA", "Brand CTA for Detara"),
            ("cta.explore_luxora_glow", "EXPLORE LUXORA GLOW", "Brand CTA for Luxora Glow"),
            ("cta.visit_benavi", "VISIT BENAVI", "Brand CTA for Benavi"),
            ("cta.explore_rupaari", "EXPLORE RUPAARI", "Brand CTA for Rupaari"),
            ("cta.explore_case_suno", "EXPLORE CASE SUNO", "Brand CTA for Case Suno"),
            ("cta.create_your_zemo", "CREATE YOUR ZEMO", "Brand CTA for Zemo"),
            ("form.error.email_invalid", "Please enter a valid corporate email address.", "Form validation message"),
            ("form.error.required", "This field is required.", "Form required field validation"),
            ("form.enquiry.success", "Thank you for reaching out. Your enquiry has been received and routed.", "Enquiry success text"),
            ("nav.partner_with_skad", "PARTNER WITH SKAD", "Navigation bar CTA"),
            ("cookie_banner.text", "We use essential cookies to maintain corporate security and evaluate platform traffic.", "Cookie notice"),
            ("404.headline", "Page Not Found", "404 Error page title"),
            ("404.message", "The corporate resource or entity page you requested does not exist.", "404 Error message"),
        ]
        for key, value, desc in ui_strings_data:
            UIString.objects.get_or_create(
                key=key,
                defaults={"value": value, "description": desc},
            )

        # 13. Seed Global Site Settings (Doc 2 Page 3 & 16)
        SiteSettings.objects.get_or_create(
            group_name="SKAD GROUP",
            defaults={
                "primary_headline": "BUILDING BUSINESSES. CREATING BRANDS. SHAPING THE FUTURE.",
                "operating_philosophy": "BUILD • CONNECT • SCALE",
                "primary_email": "contact@skadgroup.com",
                "support_phone": "+91 261 000 0000",
                "copyright_text": "© 2026 SKAD GROUP. All rights reserved.",
                "social_links": {
                    "linkedin": "https://linkedin.com/company/skadgroup",
                    "twitter": "https://x.com/skadgroup",
                },
                "maintenance_mode": False,
            },
        )

        # 14. Seed Primary Navigation Items (Doc 2 Page 3, 4, 16)
        nav_tree = [
            ("GROUP", "/about", 1, [
                ("Our Story", "/our-story", 1),
                ("Strategy", "/strategy", 2),
                ("Governance", "/documents", 3),
            ]),
            ("COMPANIES", "/companies", 2, [
                ("SKAD Jewels India", "/companies/skad-jewels", 1),
                ("Luxora Glow Essentials", "/companies/luxora-glow-essentials", 2),
                ("Detara Ltd", "/companies/detara-ltd", 3),
                ("SKAD Diatech Exports", "/companies/skad-diatech-exports", 4),
            ]),
            ("BRANDS", "/brands", 3, [
                ("DETARA", "/brands/detara", 1),
                ("LUXORA GLOW", "/brands/luxora-glow", 2),
                ("BENAVI", "/brands/benavi", 3),
                ("RUPAARI", "/brands/rupaari", 4),
                ("CASE SUNO", "/brands/case-suno", 5),
                ("ZEMO", "/brands/zemo", 6),
            ]),
            ("PLATFORMS & VENTURES", "/platforms", 4, [
                ("SKAD CommerceOS", "/platforms/skad-commerceos", 1),
                ("SKAD Commerce Lab", "/platforms/skad-commerce-lab", 2),
                ("Future Ventures", "/ventures", 3),
            ]),
            ("CAPABILITIES", "/capabilities", 5, []),
            ("IMPACT", "/impact", 6, [
                ("Kalla Rudra Foundation", "/impact/kalla-rudra-foundation", 1),
            ]),
            ("INSIGHTS", "/insights", 7, [
                ("Newsroom", "/newsroom", 1),
                ("Reports", "/reports", 2),
            ]),
            ("PEOPLE", "/people", 8, [
                ("Leadership", "/leadership", 1),
                ("Culture", "/culture", 2),
            ]),
            ("PARTNERS", "/partners", 9, []),
            ("CONTACT", "/contact", 10, []),
        ]
        for label, link, order, children in nav_tree:
            parent_item, _ = NavigationItem.objects.get_or_create(
                label=label,
                defaults={"link": link, "order": order, "visible": True},
            )
            for ch_label, ch_link, ch_order in children:
                NavigationItem.objects.get_or_create(
                    label=ch_label,
                    parent=parent_item,
                    defaults={"link": ch_link, "order": ch_order, "visible": True},
                )

        # 15. Seed Footer Columns (Doc 2 Page 16)
        footer_data = [
            ("GROUP", 1, [{"label": "About", "href": "/about"}, {"label": "Strategy", "href": "/strategy"}, {"label": "Leadership", "href": "/people"}]),
            ("COMPANIES", 2, [{"label": "SKAD Jewels India", "href": "/companies/skad-jewels"}, {"label": "Luxora Glow Essentials", "href": "/companies/luxora-glow-essentials"}, {"label": "Detara Ltd", "href": "/companies/detara-ltd"}, {"label": "SKAD Diatech Exports", "href": "/companies/skad-diatech-exports"}]),
            ("BRANDS", 3, [{"label": "DETARA", "href": "/brands/detara"}, {"label": "LUXORA GLOW", "href": "/brands/luxora-glow"}, {"label": "BENAVI", "href": "/brands/benavi"}, {"label": "ZEMO", "href": "/brands/zemo"}]),
            ("PLATFORMS", 4, [{"label": "CommerceOS", "href": "/platforms/skad-commerceos"}, {"label": "Commerce Lab", "href": "/platforms/skad-commerce-lab"}, {"label": "Future Ventures", "href": "/ventures"}]),
            ("LEGAL & TRUST", 5, [{"label": "Privacy Policy", "href": "/documents"}, {"label": "Terms of Use", "href": "/documents"}, {"label": "Code of Conduct", "href": "/documents"}]),
        ]
        for title, order, links in footer_data:
            FooterColumn.objects.get_or_create(
                title=title,
                defaults={"order": order, "links": links},
            )

        # 16. Seed Canonical Homepage & Typed Sections (Doc 2 Page 3-4, 14-15)
        home_page, _ = Page.objects.get_or_create(
            slug="home",
            defaults={
                "title": "SKAD GROUP | Corporate Homepage",
                "template": "home",
                "status": PublishStatus.DRAFT,
                "verified": False,
                "seo_title": "SKAD GROUP | Building Businesses. Creating Brands. Shaping the Future.",
                "seo_description": "SKAD GROUP is a diversified corporate ecosystem building companies, brands, and platforms across international markets.",
            },
        )
        sections_data = [
            ("hero", 1, "navy", {
                "headline_lines": ["BUILDING BUSINESSES.", "CREATING BRANDS.", "SHAPING THE FUTURE."],
                "supporting_copy": "SKAD GROUP is a diversified business group building companies, brands, technology platforms and entrepreneurial ventures across markets.",
                "primary_cta": {"label": "EXPLORE THE GROUP", "kind": "page", "target": "about", "open_in_new_tab": False},
                "secondary_cta": {"label": "PARTNER WITH SKAD", "kind": "page", "target": "contact", "open_in_new_tab": False},
                "show_infinity_animation": True,
            }),
            ("group_intro", 2, "white", {
                "lead_statement": "BUILD • CONNECT • SCALE",
                "description": "Short group introduction and BUILD / CONNECT / SCALE pillars.",
                "pillars": [
                    {"pillar": "BUILD", "meaning": "Create new business assets", "example": "Companies, brands, products, platforms"},
                    {"pillar": "CONNECT", "meaning": "Connect capabilities and markets", "example": "Manufacturing + technology + talent + international trade"},
                    {"pillar": "SCALE", "meaning": "Turn validated assets into repeatable growth", "example": "Processes, data, automation, commerce infrastructure"},
                ],
            }),
            ("at_a_glance", 3, "offwhite", {
                "title": "SKAD at a Glance",
                "items": [
                    {"label": "Group Philosophy", "value": "BUILD • CONNECT • SCALE"},
                    {"label": "Core Hubs", "value": "India, United Kingdom, Middle East"},
                ],
            }),
            ("companies", 4, "white", {"title": "Our Companies", "description": "Distinct corporate legal entities operating across manufacturing, trade, and services."}),
            ("brands", 5, "white", {"title": "Our Brands", "description": "Consumer and market brands each maintaining an independent identity."}),
            ("platforms", 6, "offwhite", {"title": "Platforms & Ventures", "description": "CommerceOS, Commerce Lab and future entrepreneurial ventures."}),
            ("ecosystem", 7, "navy", {"title": "Interactive SKAD Ecosystem", "description": "Visual, navigable architecture connecting Group, Companies, Brands, Platforms, and Foundation.", "show_graph": True}),
            ("value_pillars", 8, "white", {"title": "How We Create Value", "pillars": []}),
            ("capabilities", 9, "white", {"title": "Our Capabilities", "description": "Product, Brand, Technology, Commerce, Manufacturing, Trade, AI, Growth."}),
            ("contact", 10, "navy", {
                "heading": "Partner With SKAD",
                "supporting_text": "Connect with our corporate leadership across commerce, trade, and strategic partnerships.",
                "cta_button": {"label": "START A CONVERSATION", "kind": "page", "target": "contact", "open_in_new_tab": False},
            }),
        ]
        for stype, sorder, sbg, scontent in sections_data:
            Section.objects.get_or_create(
                page=home_page,
                type=stype,
                defaults={
                    "order": sorder,
                    "background": sbg,
                    "content": scontent,
                    "enabled": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Canonical SKAD GROUP structure seeded successfully! (All items draft/unverified)"))

