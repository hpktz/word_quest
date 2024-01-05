function change_time() {
    const start = document.getElementsByClassName('date-start-input')[0];
    const end = document.getElementsByClassName('date-end-input')[0];

    var isThere = false;
    for (let i = 0; i < document.getElementsByClassName('list-box').length; i++) {
        var list_creation = document.getElementsByClassName('list-box')[i].dataset.list_creation;
        var dateISO = list_creation.split('/').reverse().join('-');
        list_creation = new Date(Date.parse(dateISO));
        list_creation = list_creation.getTime() / 1000;

        console.log(start.value);
        var startDate = new Date(start.value);
        startDate = startDate.getTime() / 1000;

        console.log(end.value);
        var endDate = new Date(end.value);
        endDate = endDate.getTime() / 1000;

        console.log(startDate);
        console.log(endDate);
        console.log(list_creation);

        if (Number(list_creation) >= startDate && Number(list_creation) <= endDate) {
            document.getElementsByClassName('list-box')[i].style.display = 'block';
            isThere = true;
        } else {
            document.getElementsByClassName('list-box')[i].style.display = 'none';
        }

        if (isThere == false) {
            document.getElementsByClassName('list-box-empty')[0].style.display = 'block';
        } else {
            document.getElementsByClassName('list-box-empty')[0].style.display = 'none';
        }
    }
}

function filter_by(el) {
    console.log(el.value);

    var filter = el.value;
    var emptybox = document.getElementsByClassName('list-box-empty')[0];

    var lists = document.getElementsByClassName('list-box');
    lists = Array.from(lists);
    if (filter == "date-increasing") {
        lists.sort(function(a, b) {
            var aDate = Date(Date.parse(a.dataset.list_creation.split('/').reverse().join('-')));
            var bDate = Date(Date.parse(b.dataset.list_creation.split('/').reverse().join('-')));

            return aDate - bDate;
        });
    } else if (filter == "date-decreasing") {
        lists.sort(function(a, b) {
            var aDate = Date(Date.parse(a.dataset.list_creation.split('/').reverse().join('-')));
            var bDate = Date(Date.parse(b.dataset.list_creation.split('/').reverse().join('-')));

            return bDate - aDate;
        });
    } else if (filter == "name-increasing") {
        lists.sort(function(a, b) {
            var Aletter = a.dataset.list_name;
            Aletter = Aletter[0].toUpperCase();
            var Bletter = b.dataset.list_name;
            Bletter = Bletter[0].toUpperCase();

            return Aletter.localeCompare(Bletter);
        });
    } else if (filter == "name-decreasing") {
        lists.sort(function(a, b) {
            var Aletter = a.dataset.list_name;
            Aletter = Aletter[0].toUpperCase();
            var Bletter = b.dataset.list_name;
            Bletter = Bletter[0].toUpperCase();

            return Bletter.localeCompare(Aletter);
        });
    }
    lists.forEach(function(div) {
        div.remove();
    });

    lists.forEach(function(div) {
        document.getElementById('lists-container').insertBefore(div, emptybox);
    });
}