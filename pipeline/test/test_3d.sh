img_b64_str=$(base64 -w 0 "/home/ubuntu/Xin_Fan/CUBE-MT/pipeline/test/inputs/test.png")
printf '{ "image": "%s" }\n' "$img_b64_str" > payload.json

curl -X POST "http://localhost:8080/generate" \
  -H "Content-Type: application/json" \
  --data-binary @payload.json \
  -o output.glb
