const express = require('express')
const app = express()
const port = 3000
var XMLHttpRequest = require('xhr2');
var xhr = new XMLHttpRequest();
var sender_id = "";

require('dotenv').config();

// Só uso pra teste mesmo 
app.get('/', (req, res) => {
  res.send('Hello World!')
})

// Comunicação com a custom action action_greet, essa action manda um request e o 
// id da conversa(usuario) é armazenado
app.get('/sender/:id', (req, res) => {
    sender_id = req.params.id
    res.send(req.params.id)
    console.log(sender_id)
})
  
// Quando é requisitado uma autenticação do spotify, é redirecionado pra cá, onde é forçado um 
// envio de código no formato intent para o rasa..
app.get('/code', (req, res) => {
    var url = process.env.URL_DEEP_LINK+sender_id+"/trigger_intent?output_channel=telegram";

    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "text/plain");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      console.log('hey!')  
      // console.log(xhr.responseText);
    }};
    var data = `{
            "name": "say_code_intent",
            "entities": {
              "code": "${req.query.code}"
            }
        }`;
    xhr.send(data);
    //pensar num redirect...
    res.send('Pode voltar pro telegram :D')

})

// teste?! 
app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})