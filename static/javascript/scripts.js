document.addEventListener("DOMContentLoaded", function(){
    console.log("hello world");
    let btn = document.querySelector('input[type=submit]');
    btn.addEventListener('click', async function(event){
        event.preventDefault(); //предотвращение события по умолчанию
        let username = document.querySelector('input[name=username]').value;
        let password = document.querySelector('input[name=password]').value;

        // неблокирующий вызов http запроса
        let response = await fetch("/login", {
            method: "POST",
            // body: new FormData(document.querySelector('form'))
            headers: {'Content-Type': 'application/json'},
            body: `{"username": "${username}", "password": "${password}"}`
        });

        let response_json = await response.json();
        console.log(response_json)

        let body = document.querySelector('body');
        body.style.backgroundColor = "white";
        body.style.display = "block";
        body.innerHTML = response_json.message;
    })
})