from baml_client import b

resume = b.ExtractResume("...")
resume.experience

stream = b.stream.ExtractResume("...")

for chunk in stream:
    print(chunk.email)

done = stream.get_final_response()
done.email
