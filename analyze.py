from sklearn.cluster import KMeans
import json
import google.generativeai as genai
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def analyze_data():
    
    json_path = '/Users/oguzhanatmaca/Desktop/entrapeer/task3/all_corporate_data.json'
    new_json_path = '/Users/oguzhanatmaca/Desktop/entrapeer/task3/cluster.json'  # making JSON Cluster
    cluster_results_path = '/Users/oguzhanatmaca/Desktop/entrapeer/task3/json2.json'  #making JSON just cluster results

    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Updated data
        if isinstance(data, dict) and "updated_data" in data:
            data = data["updated_data"]
        elif not isinstance(data, list):
            print("Error: Unexpected JSON structure. Expected a list or 'updated_data' key.")
            return []
    
    except FileNotFoundError:
        print(f"Error: JSON file not found at {json_path}.")
        return []
    
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Please check the file format.")
        return []

    
    features = []
    company_details = []

    for company_data in data:
        try:
            company = company_data.get('data', {}).get('corporate', {})
            
            # Partners_count
            name_length = len(company.get('name', ''))
            description_length = len(company.get('description', ''))
            partners_count = company.get('startup_partners_count', 0)
            
            # Partner_name_length
            partners = company.get('startup_partners', [])
            avg_partner_name_length = sum(len(partner.get('company_name', '')) for partner in partners) / (len(partners) or 1)
            
            # Themes 
            themes = company.get('startup_themes', [])
            themes_count = len(themes)

             
            features.append([name_length, description_length, partners_count, avg_partner_name_length, themes_count])
            
            # Combined all features
            company_details.append({
                "name": company.get('name', 'Unknown'),
                "name_length": name_length,
                "description_length": description_length,
                "partners_count": partners_count,
                "avg_partner_name_length": avg_partner_name_length,
                "themes_count": themes_count
            })
        
        except Exception as e:
            print(f"Error processing data: {e}")

    # KMeans 
    if features:
        features = [list(map(float, f)) for f in features]  # This one is important; making string to float
        kmeans = KMeans(n_clusters=5)  # Cluster number or maybe adding random state to be stabilize
        kmeans.fit(features)
        clusters = kmeans.labels_

        
        cluster_results = []
        for idx, company in enumerate(company_details):
            company['cluster'] = int(clusters[idx])  # For Json data transfering Integer(INT)
            print(f"Şirket: {company['name']}, İsim uzunluğu = {company['name_length']}, "
                  f"Açıklama uzunluğu = {company['description_length']}, Ortak sayısı = {company['partners_count']}, "
                  f"Ortalama ortak isim uzunluğu = {company['avg_partner_name_length']:.2f}, "
                  f"Tema sayısı = {company['themes_count']}, Küme = {company['cluster']}")
            
            # Cluster results
            cluster_results.append({
                "company_name": company['name'],
                "cluster": company['cluster']
            })

        # Company informationss
        detailed_results = {
            "clustered_companies": company_details
        }

        
        try:
            with open(new_json_path, 'w') as f:
                json.dump(detailed_results, f, indent=4)
            print(f"\nKüme sonuçları ve şirket verileri yeni JSON dosyasına başarıyla kaydedildi: {new_json_path}")
        except Exception as e:
            print(f"Error writing to new JSON file: {e}")

        
        try:
            with open(cluster_results_path, 'w') as f:
                json.dump({"clusters_results": cluster_results}, f, indent=4)
            print(f"\nCluster sonuçları {cluster_results_path} dosyasına başarıyla kaydedildi.")
        except Exception as e:
            print(f"Error writing to cluster results JSON file: {e}")

        
        plot_clusters(features, clusters)

        # Google Gemini API 
        try:
            GOOGLE_API_KEY = 'AIzaSyAuUZrftqbyxtH6cRa4xHPiQLgDLiOnNUM'  # Google API KEY
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-pro')

            # For try to make description
            clusters_info = {i: [] for i in range(5)}  

            for company in company_details:
                clusters_info[company['cluster']].append(company)

            
            for cluster_id, companies in clusters_info.items():
                prompt = f"Given the following companies in cluster {cluster_id}, provide a brief description and a title for this cluster:\n\n{json.dumps(companies)}"
                response = model.generate_content(prompt)

                print(f"\nCluster {cluster_id} - Title and Description:")
                print(response.text)

        except Exception as e:
            print(f"Error calling Google Gemini API: {e}")

        return clusters
    else:
        print("Error: Data not loaded correctly or 'features' list is empty.")
        return []

def plot_clusters(features, clusters):
    
    features = np.array(features)
    clusters = np.array(clusters)

    
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(features)

    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=reduced_features[:, 0], y=reduced_features[:, 1], hue=clusters, palette="viridis", s=100)
    plt.title("Company Clusters Visualization")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.legend(title='Cluster', loc='upper right')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    analyze_data()
