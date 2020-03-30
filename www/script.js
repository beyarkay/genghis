// jQuery
$(document).ready(function () {
// Add in the node details

    // Update the `Battles Today` card
    let ul = document.getElementById("schedule");
    ul.innerHTML = "";
    const times = [
        "07h50 to 07h55",
        "08h50 to 08h55",
        "09h50 to 09h55",
        "10h50 to 10h55",
        "11h50 to 11h55",
        "12h50 to 12h55",
        "13h50 to 13h55",
        "14h50 to 14h55",
        "15h50 to 15h55",
        "16h50 to 16h55"
    ];
    const d = new Date();
    for (let i = 0; i < times.length; i++) {
        const li = document.createElement("li");
        li.appendChild(document.createTextNode(times[i]));
        li.className = "battleTime";
        if (parseInt(times[i].substring(0, 3)) < d.getHours() ||
            (parseInt(times[i].substring(0, 3)) === d.getHours() && d.getMinutes() >= 55)) {
            li.className += " strikeout"
        }
        ul.appendChild(li);
    }

    // Update the `Status` card
    let statusCard = document.getElementById('statusCard');
    statusCard.innerHTML = `<b>Status:</b><br>`;
    if (d.getMinutes() >= 50 && d.getMinutes() < 55 && d.getHours() <= 16 && d.getHours() >= 7) {
        statusCard.innerHTML +=
            `Battle In Progress<br>${55 - d.getMinutes()}m${d.getSeconds()}s left in this round`
    } else {
        statusCard.innerHTML += `No Battle right now`
    }

    // Get the gamestate.json from the server:
    function loadWithGamestate(gamestate) {
        // Update the items with Student Number
        let title = document.getElementById("mainTitle");
        const sn = gamestate['self'];
        title.innerHTML = `<h2 id="mainTitle">Bot Battle on <a href="https://people.cs.uct.ac.za/~${sn}/genghis/">${sn}</a></h2>`;
        document.title = `${sn} | Genghis Battle System`;

        // Update the Bots Card with the details of the current bots
        let divBots = document.getElementById("divBots");
        divBots.innerHTML = "";
        for (let bot_key in gamestate['bots']) {

            // Build the shadow div and add the ul/header to it
            const divShadow = document.createElement("div");
            divShadow.className = "shadow shadow-1";

            // Add the title to the bot's card
            const botTitle = document.createElement("b");
            const a = document.createElement("a");
            const sn = gamestate['bots'][bot_key]['student_number'];
            a.setAttribute('href', `https://people.cs.uct.ac.za/~${sn}/genghis/`);
            a.innerHTML = gamestate['bots'][bot_key]['student_number'];
            botTitle.appendChild(a);
            const default_icon = gamestate['bots'][bot_key]['default_icon'];
            botTitle.appendChild(document.createTextNode(` (${default_icon})`));
            divShadow.appendChild(botTitle);

            // Add a subtitle for the coins
            const b = document.createElement("b");
            b.innerHTML = "Coins: ";
            divShadow.appendChild(b);

            // Build up the ul of all the bot's coins
            const ul = document.createElement("ul");
            for (let coin in gamestate['bots'][bot_key]['coins']) {
                const li = document.createElement("li");
                li.appendChild(document.createTextNode(`${gamestate['bots'][bot_key]['coins'][coin]} x ${coin}`));

                ul.appendChild(li);
            }
            divShadow.appendChild(ul);

            // Build the PureCSS div and add the shadow div to it
            const divPure = document.createElement("div");
            divPure.className = "pure-u-1-2 pure-u-lg-1-2 pure-u-md-1-4";
            divPure.appendChild(divShadow);

            // Finally, add the pure div to divBots
            divBots.appendChild(divPure);
        }

        // Now populate the Ports card
        let divPorts = document.getElementById("divPorts");
        divPorts.innerHTML = "";

        const b = document.createElement("b");
        b.innerText = "Ports:";
        divPorts.appendChild(b);

        const ul = document.createElement("ul");
        for (let port_key in gamestate['ports']) {
            const li = document.createElement("li");
            // First create and add the normal text
            let textNode = document.createTextNode(`Port ${port_key} goes to `);
            li.appendChild(textNode);

            // Now create and add the link
            const a = document.createElement("a");
            a.setAttribute('href', `https://people.cs.uct.ac.za/~${gamestate['ports'][port_key]}/genghis/`);
            a.innerHTML = gamestate['ports'][port_key];
            li.appendChild(a);
            li.className = "port";
            // TODO check if the port works, and then add a notWorking class to it
            // if (false) {
            //     li.className += " notWorking";
            // }

            // Finally add the li to ul
            ul.appendChild(li);
        }
        divPorts.appendChild(ul)

        // Now update the gamestate card:
        let gamestateCard = document.getElementById('gamestateCard');
        gamestateCard.innerHTML = `<br>${JSON.stringify(gamestate, null, 2)}`;


    }

    function loadWithLayout(layout_string, gamestate) {
        let battleground = document.getElementById("battleground");
        battleground.innerHTML = "";
        console.log(layout_string);
        let array = layout_string.split(/\r?\n/);
        const valid_ports = [
            '0', '1', '2', '3', '4',
            '5', '6', '7', '8', '9'
        ];

        for (let i = 0; i < array.length; i++) {
            const row = document.createElement('tr');
            for (let j = 0; j < array[i].length; j++) {
                let cell = document.createElement('td');
                cell.setAttribute("class", "battleCell");
                //TODO Hyperlink the port to the node that it belongs to

                if (valid_ports.includes(array[i].charAt(j))) {
                    const a = document.createElement("a");
                    const sn = gamestate['ports'][array[i].charAt(j)];
                    a.setAttribute('href', `https://people.cs.uct.ac.za/~${sn}/genghis/`);
                    a.innerHTML = array[i].charAt(j);
                    // botTitle.appendChild(a);

                    cell.appendChild(a);
                } else {
                    cell.textContent = array[i].charAt(j);
                }
                row.appendChild(cell);
            }
            battleground.appendChild(row);
        }
    }

    let interval = 250;
    $.ajaxSetup({cache: false});

    function loadMap() {
        $.when($.ajax('vars/gamestate.json'), $.ajax('vars/layout.txt'))
            .then(function (gamestateResponse, layoutResponse) {
                // Each argument is an array with the following structure: [ data, statusText, jqXHR ]
                loadWithGamestate(gamestateResponse[0]);
                loadWithLayout(layoutResponse[0], gamestateResponse[0]);

            }, function () {
                console.log('Error while loading gamestate/layout');
            });
        setTimeout(loadMap, interval);
    }

    setTimeout(loadMap, interval);

});
