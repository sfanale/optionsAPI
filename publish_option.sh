rm function.zip
cp -a get_options_prices.py function
cd function
zip –X –r ../index.zip *
cd ..
aws lambda update-function-code --function-name options --zip-file fileb://function.zip