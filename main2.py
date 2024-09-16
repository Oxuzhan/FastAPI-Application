from fastapi import FastAPI, HTTPException
from celery.result import AsyncResult
from celery1 import app as celery_app  # Celery application
from analyze import analyze_data  # analyze.py
import requests
import os
import json
import google.generativeai as genai
# uvicorn main2:app --host 0.0.0.0 --port 8000

json_path = '/Users/oguzhanatmaca/Desktop/entrapeer/task3/all_corporate_data.json'
cluster_json_path = '/Users/oguzhanatmaca/Desktop/entrapeer/task3/cluster.json'  
# http://ai.google.dev/api/all-methods#generative-language-api
# Google Gemini API 
gemini_api_key = os.getenv("AIzaSyAuUZrftqbyxtH6cRa4xHPiQLgDLiOnNUM") 

app = FastAPI()
def load_json_data(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)

            
            if isinstance(data, dict) and "clustered_companies" in data:
                return data["clustered_companies"]
            elif isinstance(data, list):
                return data
            else:
                raise HTTPException(status_code=500, detail="Beklenmeyen JSON yapısı.")
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"JSON dosyası bulunamadı: {filepath}")
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="JSON dosyası hatalı veya bozuk.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")

def load_cluster_json_data(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            
            
            if isinstance(data, dict) and "clustered_companies" in data:
                return data["clustered_companies"]
            else:
                raise HTTPException(status_code=500, detail="Beklenmeyen JSON yapısı.")
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Cluster JSON dosyası bulunamadı: {filepath}")
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Cluster JSON dosyası hatalı veya bozuk.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cluster JSON yüklenirken hata oluştu: {str(e)}")

def get_cluster_description_gemini(cluster_data):
    try:
        response = requests.post(
            "http://ai.google.dev/api/all-methods#generative-language-api",
            headers={
                "Authorization": f"Bearer {gemini_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": {
                    "text": f"Bu şirket kümesi: {cluster_data}."
                },
                "maxTokens": 100,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        result = response.json()
        print("API Yanıtı:", result)  
        description = result.get("text", "Başlık ve açıklama oluşturulamadı.")
        
        return description
    except requests.exceptions.HTTPError as err:
        raise HTTPException(status_code=500, detail=f"Google Gemini API çağrısı sırasında hata: {err}")
    except Exception as e:
        print(f"Google Gemini API çağrısı sırasında hata: {e}")
        return "Başlık ve açıklama oluşturulamadı."


def get_startup_by_name(company_name: str):
    try:
        companies = load_json_data(json_path)
        results = []

        for company_data in companies:
            
            startup_partners = company_data.get('data', {}).get('corporate', {}).get('startup_partners', [])
            for startup in startup_partners:
                if startup.get('company_name', '').lower() == company_name.lower():
                    results.append(startup)

        if not results:
            raise HTTPException(status_code=404, detail="Belirtilen şirket adıyla eşleşen girişim bulunamadı.")
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# startup_partners fetch
@app.get("/fetch-startup-by-name/{company_name}")
def fetch_startup_by_name(company_name: str):
    startup_info = get_startup_by_name(company_name)
    if not startup_info:
        raise HTTPException(status_code=404, detail="Belirtilen şirket adıyla eşleşen girişim bulunamadı.")
    return {"startup_info": startup_info}


# Company name
def get_company_by_name(company_name: str):
    try:
        companies = load_json_data(json_path)
        for company_data in companies:
            company = company_data.get('data', {}).get('corporate', {})
            if company.get('name', '').lower() == company_name.lower():
                return company
        raise HTTPException(status_code=404, detail="Şirket bulunamadı.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cluster.json
def get_company_by_name_from_cluster(company_name: str):
    try:
        companies = load_cluster_json_data(cluster_json_path)
        for company in companies:
            if company.get('name', '').lower() == company_name.lower():
                return company
        raise HTTPException(status_code=404, detail="Şirket bulunamadı.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assign-cluster-names/")
def assign_cluster_names_endpoint():
    """Cluster isimlendirme ve açıklama ekleme işlemini yapar."""

    try:
    
        # Cluster 
        clusters = load_cluster_json_data(cluster_json_path)

        
        cluster_groups = {}
        for company in clusters:
            cluster_id = company.get('cluster')
            if cluster_id not in cluster_groups:
                cluster_groups[cluster_id] = []
            cluster_groups[cluster_id].append(company['name'])
        
        
        updated_clusters = []
        for cluster_id, company_names in cluster_groups.items():
            description = get_cluster_description_gemini(company_names)  
            updated_clusters.append({
                "cluster_id": cluster_id,
                # "description": response.text ,
                "companies": company_names
            })

        return {"message": "Cluster isimleri ve açıklamaları başarıyla eklendi.", "updated_clusters": updated_clusters}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cluster isimlendirme işlemi sırasında hata oluştu: {str(e)}")

#Endpoints

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Application!"}


@app.get("/fetch-data-by-name/{company_name}")
def fetch_data_by_name(company_name: str):
    company_info = get_company_by_name(company_name)
    if not company_info:
        raise HTTPException(status_code=404, detail="Şirket bulunamadı.")
    task = celery_app.send_task('celery1.print_company_name', args=[company_info['name']])
    return {"company_info": company_info}


@app.get("/fetch-clustered-data-by-name/{company_name}")
def fetch_clustered_data_by_name(company_name: str):
    company_info = get_company_by_name_from_cluster(company_name)
    if not company_info:
        raise HTTPException(status_code=404, detail="Şirket bulunamadı.")
    return {"company_info": company_info}


@app.get("/analyze-data/")
def analyze_data_endpoint():
    try:
        clustered_data = load_cluster_json_data(cluster_json_path)
        return {"clustered_companies": clustered_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz işlemi sırasında hata oluştu: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
