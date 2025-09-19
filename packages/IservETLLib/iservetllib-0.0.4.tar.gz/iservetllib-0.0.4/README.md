# **Библиотека для ETL** # 

Для формирования xlsx отчета из нескольких csv файлов.

## Разработка ##

    source venv/bin/activate

## Установка ##

    pip install IservETLLib

## Использование ##

python3 ./src/IservETLLib/index.py

## Сборка ##

python3 -m build
python3 -m twine upload --repository pypi dist/*