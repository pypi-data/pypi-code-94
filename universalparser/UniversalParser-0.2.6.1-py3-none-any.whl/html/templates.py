HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
    <title>${title}</title>
</head>
<body>
    ${tables}
</body>
</html>
"""

TABLE = """
<table class="table table-bordered">
    <caption></caption>
    <thead>
        ${tr_ths}
    </thead>
    <tbody>
        ${tr_tds}
    </tbody>
    <tfoot></tfoot>
</table>
"""
