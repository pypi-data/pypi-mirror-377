# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product matrix in eCommerce",
    "version": "15.0.1.0.1",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/e-commerce",
    "category": "Website",
    "maintainers": ["chienandalu"],
    "depends": [
        "sale_product_matrix",
        "website_sale",
    ],
    "data": [
        "templates/product_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_product_matrix/static/src/js/**/*.js",
            "website_sale_product_matrix/static/src/scss/**/*.scss",
        ],
    },
}
