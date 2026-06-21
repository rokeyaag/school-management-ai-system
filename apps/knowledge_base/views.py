from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Subject, Document
from .vector_engine import add_document, delete_document, search

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def subject_list(request):
    school = request.user.school
    if request.method == 'GET':
        subjects = Subject.objects.filter(school=school)
        return Response([{'id': s.id, 'name': s.name, 'name_bn': s.name_bn, 'class_name': s.class_name} for s in subjects])
    subject = Subject.objects.create(
        school=school,
        name=request.data.get('name'),
        name_bn=request.data.get('name_bn', ''),
        class_name=request.data.get('class_name', ''),
    )
    return Response({'id': subject.id, 'name': subject.name}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def document_list(request):
    school = request.user.school
    if request.method == 'GET':
        subject_id = request.query_params.get('subject')
        docs = Document.objects.filter(school=school).select_related('subject')
        if subject_id:
            docs = docs.filter(subject_id=subject_id)
        return Response([{
            'id': d.id, 'title': d.title, 'subject': d.subject.name,
            'status': d.status, 'chunk_count': d.chunk_count,
            'created_at': d.created_at,
        } for d in docs])
    # POST - create + ingest
    subject_id = request.data.get('subject_id')
    title = request.data.get('title')
    raw_text = request.data.get('raw_text', '')
    if not subject_id or not title or not raw_text:
        return Response({'error': 'subject_id, title, raw_text required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        subject = Subject.objects.get(id=subject_id, school=school)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
    doc = Document.objects.create(
        school=school, subject=subject, title=title, raw_text=raw_text,
        status='processing', uploaded_by=request.user
    )
    try:
        chunk_count = add_document(doc)
        doc.status = 'ready'
        doc.chunk_count = chunk_count
        doc.save()
    except Exception as e:
        doc.status = 'failed'
        doc.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'id': doc.id, 'title': doc.title, 'chunk_count': doc.chunk_count, 'status': doc.status}, status=status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def document_detail(request, pk):
    try:
        doc = Document.objects.get(id=pk, school=request.user.school)
    except Document.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response({'id': doc.id, 'title': doc.title, 'subject': doc.subject.name, 'raw_text': doc.raw_text, 'chunk_count': doc.chunk_count, 'status': doc.status})
    delete_document(doc.id)
    doc.delete()
    return Response({'message': 'Deleted'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_textbook(request):
    school = request.user.school
    query = request.data.get('query')
    subject_id = request.data.get('subject_id')
    lang = request.data.get('lang', 'en')
    if not query:
        return Response({'error': 'query required'}, status=status.HTTP_400_BAD_REQUEST)

    results = search(query, school.id, subject_id, n_results=4)
    if not results:
        msg = 'কোনো প্রাসঙ্গিক তথ্য পাওয়া যায়নি। প্রথমে বইয়ের কন্টেন্ট আপলোড করুন।' if lang == 'bn' else 'No relevant content found. Please upload textbook content first.'
        return Response({'answer': msg, 'sources': []})

    context = '\n\n---\n\n'.join([r['text'] for r in results])
    sources = list(set([r['meta']['document_title'] for r in results]))

    if lang == 'bn':
        prompt = f'''Tumi ekjon sohayok shikkhok. Niche boi-er ongsho gulo babohar kore sikkharthir proshner uttor dao. Sudhumatro deya tothyer vittite uttor dao, nije theke tothyo banio na.

Boi-er ongsho:
{context}

Sikkharthir proshno: {query}

Sohoj o spasto bhashay banglay uttor dao.'''
    else:
        prompt = f'''You are a helpful teacher. Use the textbook excerpts below to answer the student question. Only answer based on the given content, do not make up information.

Textbook excerpts:
{context}

Student question: {query}

Provide a clear, simple answer.'''

    from apps.ai_engine.groq_client import chat
    answer = chat([{'role': 'user', 'content': prompt}])
    return Response({'answer': answer, 'sources': sources})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_pdf(request):
    school = request.user.school
    subject_id = request.data.get('subject_id')
    title = request.data.get('title')
    file = request.FILES.get('file')

    if not subject_id or not title or not file:
        return Response({'error': 'subject_id, title, file required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        subject = Subject.objects.get(id=subject_id, school=school)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        raw_text = '\n'.join(text_parts)
    except Exception as e:
        return Response({'error': f'Failed to read PDF: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    if not raw_text.strip():
        return Response({'error': 'No extractable text found in PDF (might be scanned images)'}, status=status.HTTP_400_BAD_REQUEST)

    doc = Document.objects.create(
        school=school, subject=subject, title=title, raw_text=raw_text,
        status='processing', uploaded_by=request.user
    )
    try:
        chunk_count = add_document(doc)
        doc.status = 'ready'
        doc.chunk_count = chunk_count
        doc.save()
    except Exception as e:
        doc.status = 'failed'
        doc.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'id': doc.id, 'title': doc.title, 'chunk_count': doc.chunk_count, 'status': doc.status, 'text_length': len(raw_text)}, status=status.HTTP_201_CREATED)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    import base64
    school = request.user.school
    subject_id = request.data.get('subject_id')
    title = request.data.get('title')
    file = request.FILES.get('file')
    lang = request.data.get('lang', 'en')

    if not subject_id or not title or not file:
        return Response({'error': 'subject_id, title, file required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        subject = Subject.objects.get(id=subject_id, school=school)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        image_bytes = file.read()
        b64_image = base64.b64encode(image_bytes).decode('utf-8')
        mime_type = file.content_type or 'image/jpeg'

        from groq import Groq
        from decouple import config
        client = Groq(api_key=config('GROQ_API_KEY'))

        if lang == 'bn':
            instruction = 'এই বইয়ের পাতার ছবি থেকে সব টেক্সট হুবহু বের করো। শুধুমাত্র টেক্সট দাও, কোনো ব্যাখ্যা বা মন্তব্য দিও না।'
        else:
            instruction = 'Extract all text from this textbook page image exactly as written. Only return the extracted text, no explanation or commentary.'

        response = client.chat.completions.create(
            model='meta-llama/llama-4-scout-17b-16e-instruct',
            messages=[{
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': instruction},
                    {'type': 'image_url', 'image_url': {'url': f'data:{mime_type};base64,{b64_image}'}}
                ]
            }],
            max_tokens=2048,
            temperature=0.1,
        )
        raw_text = response.choices[0].message.content
    except Exception as e:
        return Response({'error': f'Failed to read image: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    if not raw_text or not raw_text.strip():
        return Response({'error': 'No text could be extracted from the image'}, status=status.HTTP_400_BAD_REQUEST)

    doc = Document.objects.create(
        school=school, subject=subject, title=title, raw_text=raw_text,
        status='processing', uploaded_by=request.user
    )
    try:
        chunk_count = add_document(doc)
        doc.status = 'ready'
        doc.chunk_count = chunk_count
        doc.save()
    except Exception as e:
        doc.status = 'failed'
        doc.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'id': doc.id, 'title': doc.title, 'chunk_count': doc.chunk_count, 'status': doc.status, 'extracted_text': raw_text}, status=status.HTTP_201_CREATED)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_scanned_pdf(request):
    import base64
    school = request.user.school
    subject_id = request.data.get('subject_id')
    title = request.data.get('title')
    file = request.FILES.get('file')
    lang = request.data.get('lang', 'en')

    if not subject_id or not title or not file:
        return Response({'error': 'subject_id, title, file required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        subject = Subject.objects.get(id=subject_id, school=school)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        import pypdfium2 as pdfium
        import io
        from groq import Groq
        from decouple import config

        pdf_bytes = file.read()
        pdf = pdfium.PdfDocument(pdf_bytes)
        n_pages = len(pdf)
        max_pages = 15

        client = Groq(api_key=config('GROQ_API_KEY'))
        if lang == 'bn':
            instruction = 'এই বইয়ের পাতার ছবি থেকে সব টেক্সট হুবহু বের করো। শুধুমাত্র টেক্সট দাও, কোনো ব্যাখ্যা বা মন্তব্য দিও না।'
        else:
            instruction = 'Extract all text from this textbook page image exactly as written. Only return the extracted text, no explanation or commentary.'

        all_text = []
        for i in range(min(n_pages, max_pages)):
            page = pdf[i]
            bitmap = page.render(scale=2.0)
            pil_image = bitmap.to_pil()
            buf = io.BytesIO()
            pil_image.save(buf, format='JPEG', quality=85)
            b64_image = base64.b64encode(buf.getvalue()).decode('utf-8')

            response = client.chat.completions.create(
                model='meta-llama/llama-4-scout-17b-16e-instruct',
                messages=[{
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': instruction},
                        {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64_image}'}}
                    ]
                }],
                max_tokens=2048,
                temperature=0.1,
            )
            page_text = response.choices[0].message.content
            if page_text:
                all_text.append(f'--- Page {i+1} ---\n{page_text}')

        raw_text = '\n\n'.join(all_text)
        pdf.close()
    except Exception as e:
        return Response({'error': f'Failed to process PDF: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    if not raw_text.strip():
        return Response({'error': 'No text could be extracted from the PDF pages'}, status=status.HTTP_400_BAD_REQUEST)

    doc = Document.objects.create(
        school=school, subject=subject, title=title, raw_text=raw_text,
        status='processing', uploaded_by=request.user
    )
    try:
        chunk_count = add_document(doc)
        doc.status = 'ready'
        doc.chunk_count = chunk_count
        doc.save()
    except Exception as e:
        doc.status = 'failed'
        doc.save()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'id': doc.id, 'title': doc.title, 'chunk_count': doc.chunk_count, 'status': doc.status, 'pages_processed': min(n_pages, max_pages), 'total_pages': n_pages}, status=status.HTTP_201_CREATED)