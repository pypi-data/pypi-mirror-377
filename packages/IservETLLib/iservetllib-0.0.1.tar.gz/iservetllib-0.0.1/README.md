# **Библиотека для ETL** # 

Для формирования xlsx отчета из нескольких csv файлов.

## Разработка ##

    source venv/bin/activate

## Установка ##

    pip install IservETLLib

## Использование ##

python3 ./src/IservETLLib/index.py

<!-- python3 OUTPUT_NAME="res.xlsx" HEADERS_PATH="" META_NAME="excel.meta" SEP=;  "Опросный лист ТУ_2025-07-28_14-28-44.csv" "Опросный лист УСПД_2025-07-28_14-33-04.csv" -->

python3 -m build
python3 -m twine upload --repository pypi dist/*