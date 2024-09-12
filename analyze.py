# analyze.py

from sklearn.cluster import KMeans
import json
import os

def analyze_data():
    # JSON dosyasının dinamik yolu
    json_path = '/Users/oguzhanatmaca/Desktop/entrapeer/task3/all_corporate_data.json'
    
    # Verilerin yüklenmesi
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Özelliklerin çıkartılması
    features = []

    for company_data in data:
        try:
            company = company_data.get('data', {}).get('corporate', {})
            name_length = len(company.get('name', ''))
            description_length = len(company.get('description', ''))
            partners_count = company.get('startup_partners_count', 0)
            partners = company.get('startup_partners', [])
            avg_partner_name_length = sum(len(partner.get('company_name', '')) for partner in partners) / (len(partners) or 1)
            themes = company.get('startup_themes', [])
            themes_count = len(themes)
            features.append([name_length, description_length, partners_count, avg_partner_name_length, themes_count])
        except Exception as e:
            print(f"Veri işleme hatası: {e}")

    if features:
        features = [list(map(float, f)) for f in features]
        kmeans = KMeans(n_clusters=5)
        kmeans.fit(features)
        clusters = kmeans.labels_
        return clusters
    else:
        print("Hata: Veriler düzgün yüklenmedi veya 'features' listesi boş.")
        return []

# Ana fonksiyon
if __name__ == "__main__":
    clusters = analyze_data()
    print("Küme sonuçları:", clusters)
