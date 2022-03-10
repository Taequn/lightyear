echo "sourcing venv"
source venv/bin/activate
echo "sourced venv"

echo "starting linkedin adder"
python3 linkedin_add_main.py 
echo "finished linkedin adder"

echo "deactivating venv"
deactivate
echo "deactivated, ending"