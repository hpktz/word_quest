/**
 * Filters the list-box elements based on the selected start and end dates.
 *  -> If the list-box element's creation date is between the start and end dates, it is displayed.
 * 
 * @function change_time
 * @returns {void}
 */
const start = document.getElementsByClassName('date-start-input')[0];
const end = document.getElementsByClassName('date-end-input')[0];
start.addEventListener('change', function() {
    change_time();
});
end.addEventListener('change', function() {
    change_time();
});

function change_time() {
    var isThere = false;
    for (let i = 0; i < document.getElementsByClassName('list-box').length; i++) {
        // get the creation date of the list box
        var list_creation = document.getElementsByClassName('list-box')[i].dataset.list_creation;
        var dateISO = list_creation.split('/').reverse().join('-');
        list_creation = new Date(Date.parse(dateISO));
        list_creation = list_creation.getTime() / 1000;

        // get the start and end dates from the input elements
        var startDate = new Date(start.value);
        startDate = startDate.getTime() / 1000;

        var endDate = new Date(end.value);
        endDate = endDate.getTime() / 1000;

        // if the list box's creation date is between the start and end dates, it is displayed
        if (Number(list_creation) >= startDate && Number(list_creation) <= endDate) {
            document.getElementsByClassName('list-box')[i].style.display = 'grid';
            isThere = true;
        } else {
            document.getElementsByClassName('list-box')[i].style.display = 'none';
        }

        // if there is no list box to display, the "no list box" message is displayed
        if (isThere == false) {
            document.getElementsByClassName('list-box-empty')[0].style.display = 'grid';
        } else {
            document.getElementsByClassName('list-box-empty')[0].style.display = 'none';
        }
    }
}

/**
 * Sorts and filters the list boxes (html elements) based on the selected filter.
 *  -> If the filter is "date-increasing", the list boxes are sorted by creation date in increasing order.
 *  -> If the filter is "date-decreasing", the list boxes are sorted by creation date in decreasing order.
 *  -> If the filter is "name-increasing", the list boxes are sorted by name in increasing order.
 *  -> If the filter is "name-decreasing", the list boxes are sorted by name in decreasing order.
 * 
 * @function filter_by
 * @param {HTMLInputElement} el - The HTML input element representing the filter.
 * @returns {void}
 */
const filterSelect = document.getElementById('filter-select');
filterSelect.addEventListener('change', function() {
    filter_by(filterSelect);
});

function filter_by(el) {
    var filter = el.value;
    var emptybox = document.getElementsByClassName('list-box-empty')[0];

    // get all the list boxes
    var lists = document.getElementsByClassName('list-box');
    lists = Array.from(lists);
    // filter the list boxes based on the selected filter
    if (filter == "date-increasing") {
        lists.sort(function(a, b) {
            var aDate = new Date(a.dataset.list_creation.split('/').reverse().join('-'));
            var bDate = new Date(b.dataset.list_creation.split('/').reverse().join('-'));

            return aDate - bDate;
        });
    } else if (filter == "date-decreasing") {
        lists.sort(function(a, b) {
            var aDate = new Date(Date.parse(a.dataset.list_creation.split('/').reverse().join('-')));
            var bDate = new Date(Date.parse(b.dataset.list_creation.split('/').reverse().join('-')));

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
    // remove all the list boxes from the page
    lists.forEach(function(div) {
        div.remove();
    });
    // add the list boxes sorted and filtered to the page
    lists.forEach(function(div) {
        document.getElementById('lists-container').insertBefore(div, emptybox);
    });
}