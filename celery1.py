from celery import Celery

# Celery uygulamasını oluşturma
app = Celery(
    'tasks',
    broker='redis://localhost:6380/0',
    backend='redis://localhost:6380/0'
)

@app.task
def fetch_data(company_id):
    # Burada API çağrısını yaparak verileri kaydetme
    import requests
    import json

    url = "https://ranking.glassdollar.com/graphql"
    query = """
    query ($id: String!) {
      corporate(id: $id) {
        id
        name
        description
        logo_url
        hq_city
        hq_country
        website_url
        linkedin_url
        twitter_url
        startup_partners_count
        startup_partners {
          master_startup_id
          company_name
          logo_url: logo
          city
          website
          country
          theme_gd
          __typename
        }
        startup_themes
        startup_friendly_badge
        __typename
      }
    }
    """
    payload = {
        "query": query,
        "variables": {
            "id": company_id
        }
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Veriyi kaydetmek için dosya işlemleri
        with open(f'data_{company_id}.json', 'w') as f:
            json.dump(data, f, indent=4)
        print(f"{company_id} için veri başarıyla çekildi ve kaydedildi.")
    else:
        print(f"API isteği başarısız oldu: {company_id}, Durum Kodu: {response.status_code}")
        print("Yanıt Mesajı:", response.text)

# Yeni run_analysis görevini ekle
@app.task
def print_company_name(company_name: str):
    print(f"Company Name: {company_name}")
    return f"Company Name: {company_name}"