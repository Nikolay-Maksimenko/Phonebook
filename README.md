# Phonebook

## Описание

Телефонный справочник с консольным интерфейсом. 

Хранение данных о контактах предусмотрено в csv файле.

Модуль create_sample_data предназначен для генерации образца csv файла с контактами.

### Доступные консольные команды:

**l** - вывод постранично записей из справочника на экран

**a** - добавление новой записи в справочник

**e** - редактирование записи в справочнике

**s** - поиск записей по одной или нескольким характеристикам


Операции добавления, редактирования и поиска контактов предусматривают пользовательский ввод.

Параметры записываются в одну строку с разделением через пробел.

Пример пользовательского ввода:

``` last_name=Петров first_name=Владимир ```

### Запуск проекта в docker:

1. Создание образа проекта:

```
sudo docker build -t phonebook .
```

2. Запуск контейнера:

```
sudo docker run -it phonebook
```