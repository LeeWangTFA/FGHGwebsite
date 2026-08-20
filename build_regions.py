#!/usr/bin/env python3
"""
Build regional static pages from template/page.template.html + regions/*.json.

Usage: python3 build_regions.py

Add a new region: copy regions/_example.json, fill in real data, set "slug",
then rerun this script. Output goes to /{slug}/index.html (or root index.html
when slug is "").
"""
import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "template" / "page.template.html"
REGIONS_DIR = ROOT / "regions"
SITE_ORIGIN = "https://feelgoodhealgood.tw"

PHONE_ICON_SVG = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">'
    '<path d="M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2a1 1 0 0 1 1.01-.24c1.21.4 2.5.6 3.83.6a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1'
    'C10.16 21 3 13.84 3 5a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.33.2 2.62.6 3.83a1 1 0 0 1-.24 1.01l-2.24 2.2z"/></svg>'
)
BTN_PHONE_ICON_SVG = PHONE_ICON_SVG.replace('width="15" height="15"', 'width="14" height="14"')


def die(msg: str) -> None:
    raise SystemExit(f"錯誤：{msg}")


def check_no_placeholder(value, field: str) -> None:
    if isinstance(value, str) and "待確認" in value:
        raise ValueError(f"欄位 {field} 仍是「待確認」")
    if isinstance(value, list):
        for item in value:
            check_no_placeholder(item, field)
    if isinstance(value, dict):
        for k, v in value.items():
            if k.startswith("_"):
                continue
            check_no_placeholder(v, f"{field}.{k}")


def page_url(slug: str) -> str:
    return f"{SITE_ORIGIN}/{slug}/" if slug else f"{SITE_ORIGIN}/"


def build_contact_phone_rows(phones: list) -> str:
    lines = []
    for p in phones:
        lines.append(
            f'        <p class="contact-phone"><span class="icon-phone-gold">{PHONE_ICON_SVG}</span> '
            f'{p["num"]}　{p["name"]}</p>'
        )
    return "\n".join(lines)


def build_contact_phone_btns(phones: list) -> str:
    lines = []
    for i, p in enumerate(phones, start=1):
        lines.append(
            f'          <a href="tel:{p["tel"]}" class="btn btn-outline" data-cta-type="call" '
            f'data-cta-location="contact_phone_{i}" data-cta-label="{p["num"]}">{BTN_PHONE_ICON_SVG} {p["num"]}</a>'
        )
    return "\n".join(lines)


def build_area_list_html(groups: list) -> str:
    lines = []
    for g in groups:
        lines.append(f'          <div class="area-row"><span class="area-dot"></span><span>{g}</span></div>')
    return "\n".join(lines)


def build_price_ref_cards(examples: list) -> str:
    lines = []
    for e in examples:
        lines.append(
            '            <div class="price-ref-card">\n'
            f'              <p class="price-ref-person">{e["person"]}</p>\n'
            f'              <p class="price-ref-time">{e["time"]}</p>\n'
            f'              <p class="price-ref-route">{e["route"]}</p>\n'
            f'              <p class="price-ref-need">{e["need"]}</p>\n'
            f'              <p class="price-ref-cost">{e["cost"]}</p>\n'
            '            </div>'
        )
    return "\n".join(lines)


def build_jsonld(data: dict) -> str:
    slug = data["slug"]
    url = page_url(slug)
    phones = data["phones"]
    primary = next((p for p in phones if p.get("primary")), phones[0])

    graph = [
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": data["meta_title"],
            "inLanguage": "zh-TW",
            "isPartOf": {"@id": f"{url}#business"},
            "dateModified": data["jsonld_date_modified"],
        },
        {
            "@type": ["LocalBusiness", "MedicalBusiness"],
            "@id": f"{url}#business",
            "name": "FeelGoodHealGood",
            "alternateName": "好心情好病情無障礙接送",
            "description": "大台北地區專業無障礙輪椅接送（自費服務）與電動爬梯機上下樓服務（爬梯機適用長照2.0補助）。品牌使命：讓無法親自陪伴的家屬安心交託，守護長輩每一次出門的選擇權與尊嚴。",
            "slogan": "好心情，好病情",
            "url": url,
            "image": f"{SITE_ORIGIN}/image.jpg",
            "logo": f"{SITE_ORIGIN}/logo-icon.png",
            "priceRange": "NT$500-1500",
            "telephone": [f"+886-{p['tel'][1:4]}-{p['tel'][4:7]}-{p['tel'][7:]}" for p in phones],
            "sameAs": [f"https://line.me/R/ti/p/{data['line_oa_id']}"],
            "areaServed": (
                [{"@type": "City", "name": c} for c in data["area_served_cities"]]
                + [{"@type": "AdministrativeArea", "name": a} for a in data["area_served_admin"]]
            ),
            "serviceType": ["無障礙輪椅接送", "電動爬梯機上下樓", "洗腎回診接送", "醫院往返接送", "復健接送"],
            "contactPoint": [
                {
                    "@type": "ContactPoint",
                    "telephone": f"+886-{p['tel'][1:4]}-{p['tel'][4:7]}-{p['tel'][7:]}",
                    "contactType": "customer service",
                    "areaServed": p["areas"],
                    "availableLanguage": "zh-TW",
                    "hoursAvailable": {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                        "opens": "07:00",
                        "closes": "21:00",
                    },
                }
                for p in phones
            ],
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "服務項目",
                "itemListElement": [
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": "無障礙輪椅接送",
                            "description": "專屬無障礙車輛，適用輪椅、電動輪椅乘客。洗腎回診、就醫復健、醫院診所往返、家庭聚會出行，全程專業陪伴。費用採彈性議價。",
                        },
                    },
                    {
                        "@type": "Offer",
                        "itemOffered": {
                            "@type": "Service",
                            "name": "電動爬梯機上下樓",
                            "description": "無電梯公寓專用電動爬梯機服務。平穩安全，專業人員全程陪同。長照2.0補助適用，一般戶2樓自付310元起。",
                        },
                        "priceSpecification": {
                            "@type": "PriceSpecification",
                            "minPrice": "100",
                            "maxPrice": "1100",
                            "priceCurrency": "TWD",
                            "description": "依樓層與長照補助身份別（一般戶／中低收入／低收入）而定，2樓一般戶自付310元起，未申請補助者可選全額自費",
                        },
                    },
                ],
            },
        },
    ]
    doc = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(doc, ensure_ascii=False, indent=2)


def build_page(template: str, data: dict) -> str:
    slug = data["slug"]
    url = page_url(slug)
    phones = data["phones"]
    primary = next((p for p in phones if p.get("primary")), phones[0])

    replacements = {
        "{{META_TITLE}}": data["meta_title"],
        "{{META_DESC}}": data["meta_desc"],
        "{{CANONICAL_URL}}": url,
        "{{OG_TITLE}}": data["og_title"],
        "{{OG_DESC}}": data["og_desc"],
        "{{TWITTER_TITLE}}": data["twitter_title"],
        "{{TWITTER_DESC}}": data["twitter_desc"],
        "{{GEO_REGION}}": data["geo_region"],
        "{{GEO_PLACENAME}}": data["geo_placename"],
        "{{HERO_EYEBROW}}": data["hero_eyebrow"],
        "{{AREA_SECTION_DESC}}": data["area_section_desc"],
        "{{AREA_MAP_IMG}}": data["area_map_img"],
        "{{AREA_MAP_ALT}}": data["area_map_alt"],
        "{{AREA_LIST_HTML}}": build_area_list_html(data["area_groups"]),
        "{{AREA_NOTE}}": data["area_note"],
        "{{CONTACT_REGION_LABEL}}": data["contact_region_label"],
        "{{QR_IMG}}": data["qr_img"],
        "{{QR_ALT}}": data["qr_alt"],
        "{{LINE_URL}}": data["line_url"],
        "{{LINE_ID}}": data["line_oa_id"],
        "{{LINE_OA_HREF}}": (
            f"https://line.me/R/ti/p/{data['line_oa_id']}?oaMessage="
            f"{urllib.parse.quote(data['line_oa_message'])}"
        ),
        "{{CONTACT_PHONE_ROWS}}": build_contact_phone_rows(phones),
        "{{CONTACT_PHONE_BTNS}}": build_contact_phone_btns(phones),
        "{{PRIMARY_PHONE_TEL}}": primary["tel"],
        "{{PRICE_REF_CARDS}}": build_price_ref_cards(data["price_examples"]),
        "{{FOOTER_AREA_TEXT}}": data["footer_area_text"],
        "{{JSONLD_JSON}}": build_jsonld(data),
    }

    html = template
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    remaining = [line for line in html.splitlines() if "{{" in line]
    if remaining:
        die(f"樣板仍有未替換的 {{{{...}}}} 佔位符：{remaining}")
    return html


def main():
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    region_files = sorted(REGIONS_DIR.glob("*.json"))

    for path in region_files:
        if path.name.startswith("_"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        try:
            check_no_placeholder(data, path.stem)
        except ValueError as e:
            print(f"跳過 {path.name}：{e}")
            continue

        html = build_page(template, data)
        slug = data["slug"]
        if slug:
            out_dir = ROOT / slug
            out_dir.mkdir(exist_ok=True)
            out_path = out_dir / "index.html"
        else:
            out_path = ROOT / "index.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"已產生 {out_path.relative_to(ROOT)}（來源：{path.name}）")


if __name__ == "__main__":
    main()
