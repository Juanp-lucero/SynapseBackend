from app.services.document_processor import process_document


file_path = "uploads/a10d79f1-6f07-4830-acc9-72f6d2eee465.pdf"


text = process_document(file_path)


print("\n===================================")
print("DOCUMENTO PROCESADO")
print("===================================\n")


print("Cantidad de caracteres:")
print(len(text))


print("\nPrimeros 2000 caracteres:\n")


print(text[:2000])