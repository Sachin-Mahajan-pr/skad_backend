from drf_spectacular.openapi import AutoSchema

class SkadAutoSchema(AutoSchema):
    """
    Custom OpenAPI schema generator adding domain tags and enterprise classification.
    """
    def get_tags(self):
        tags = super().get_tags()
        path = self.path
        if "/companies" in path:
            return ["Corporate Entities - Companies"]
        elif "/brands" in path:
            return ["Consumer Brands Layer"]
        elif "/platforms" in path:
            return ["Platforms & Ventures"]
        elif "/ecosystem" in path:
            return ["Interactive Ecosystem"]
        elif "/taxonomy" in path or "/capabilities" in path or "/industries" in path or "/markets" in path:
            return ["Taxonomy & Markets"]
        elif "/enquiries" in path or "/opportunities" in path:
            return ["Inbound Inquiries & Routing"]
        elif "/careers" in path or "/applications" in path:
            return ["Careers & Talent"]
        elif "/documents" in path:
            return ["Governance & Documents"]
        elif "/seo" in path:
            return ["SEO & Discovery"]
        return tags
