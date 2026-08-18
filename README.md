# Yerel AI Doküman Asistanı (RAG)

PDF, TXT ve Markdown belgelerini sayfa bilgisi korunarak parçalayan, Ollama embedding modeliyle ChromaDB'ye kaydeden ve Llama ile kaynaklı Türkçe yanıt üreten yerel RAG uygulaması. Dosya başına 1 GB'a kadar ve 12 sayfadan büyük PDF'ler desteklenir; sabit sayfa sınırı yoktur.

## RAG akışı

1. Belgeler sayfa bazında okunur.
2. Metinler 1200 karakterlik, 200 karakter örtüşmeli parçalara ayrılır.
3. `nomic-embed-text` ile vektörler oluşturulup kalıcı ChromaDB indeksine yazılır.
4. Soruya en yakın parçalar bulunur.
5. `llama3.2:3b`, yalnızca bu bağlamı kullanarak sayfa kaynaklı cevap verir.

## Donanım ve VRAM

Varsayılan `llama3.2:3b` modeli 8 GB VRAM'li cihazlar için seçilmiştir. Uygulama bağlamı 4096 token, üretim batch'i 128 ve embedding kayıtları 32 parça ile sınırlar. Modeller iki dakika kullanılmadığında Ollama tarafından VRAM'den çıkarılabilir. Daha küçük ekran kartlarında `llama3.2:1b`, daha güçlü kartlarda daha büyük bir Llama modeli arayüzden seçilebilir.

## Kurulum

Python 3.11 veya 3.12 önerilir. Önce Ollama kurulu ve çalışıyor olmalıdır.

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Ekrandan dosya yükleyip **Yüklenenleri indeksle** düğmesine basın. Alternatif olarak dosyaları `documents/` klasörüne koyup **documents/ klasörünü tara** düğmesini kullanın.

## Proje yapısı

- `app.py`: Streamlit arayüzü
- `src/pdf_loader.py`: belge keşfi ve sayfa bazlı okuma
- `src/chunker.py`: örtüşmeli metin parçalama
- `src/embedder.py`: Ollama embedding istemcisi
- `src/vector_store.py`: kalıcı ChromaDB indeks ve benzerlik araması
- `src/llm.py`: Llama yanıt üretimi
- `src/rag.py`: uçtan uca RAG orkestrasyonu

Taranmış görüntü PDF'lerinde metin katmanı yoksa OCR gerekir; bu sürüm OCR yapmaz. Aynı adlı belge tekrar indekslendiğinde eski parçaları yenileriyle değiştirilir.

## Test

```powershell
python -m unittest discover -v
```
