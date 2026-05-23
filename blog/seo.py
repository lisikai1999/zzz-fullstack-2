from django.http import HttpResponse
from django.utils import timezone
from blog.models import Article, Tag


def sitemap_xml(request):
    base_url = request.build_absolute_uri('/').rstrip('/')
    articles = Article.objects.filter(status='published').order_by('-published_at')
    tags = Tag.objects.all()

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    xml += f'  <url>\n    <loc>{base_url}/</loc>\n'
    xml += f'    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'

    for article in articles:
        lastmod = (article.updated_at or article.published_at).strftime('%Y-%m-%d')
        xml += f'  <url>\n    <loc>{base_url}/article/{article.slug}</loc>\n'
        xml += f'    <lastmod>{lastmod}</lastmod>\n'
        xml += f'    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'

    for tag in tags:
        xml += f'  <url>\n    <loc>{base_url}/tag/{tag.slug}</loc>\n'
        xml += f'    <changefreq>weekly</changefreq>\n    <priority>0.5</priority>\n  </url>\n'

    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')


def robots_txt(request):
    base_url = request.build_absolute_uri('/').rstrip('/')
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/

Sitemap: {base_url}/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')
