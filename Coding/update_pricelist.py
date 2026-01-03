

import xmlrpc.client

url = "https://warungdesa.weha-id.com"
db = "warungdesa"
username = "admin"
password = "pelang1"



common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})


models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

pricelist_id = models.execute_kw(
    db, uid, password,
    'product.pricelist', 'search',
    [[['name', '=', 'Pasar Kemis Pricelist']]]
)

if pricelist_id:
    pricelist_id = pricelist_id[0]
    print(f"Pricelist ID: {pricelist_id}")

    products = models.execute_kw(
        db, uid, password, 
        'product.template', 'search_read',
        [[['type', '=', 'consu']]],
        {'fields': ['id', 'name', 'list_price']}    
    )
    for product in products:
        new_price = product['list_price'] 
        models.execute_kw(
            db, uid, password,
            'product.pricelist.item', 'create',
            [{
                'pricelist_id': pricelist_id,
                'display_applied_on': '1_product',
                'product_tmpl_id': product['id'],
                'compute_price': 'fixed',
                'fixed_price': new_price,
            }]
        )
        print(f"Updated price for {product['name']} to {new_price}")