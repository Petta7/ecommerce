//запросим все кнопки по классу корзины обновлений в cart.js и добавим обработчик событий в цикле.
var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)

//		создаю оператор if внутри cart.js и консольем пользователя и два разных оператора в зависимости от того,
//      вошел ли пользователь в систему или нет

        console.log('USER:', user)
        if (user == 'AnonymousUser'){
            console.log('User is not authenticated')

        }else{
            updateUserOrder(productId, action)
}

	})
}

//создаю функцию с именем updateUserOrder () и даю ей два параметра: «productId» и «action».
//Затем передам функцию в наш оператор «if», чтобы она вызывалась при входе пользователя в систему

function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		var url = '/update_item/'

		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken': csrftoken,
			},
			body:JSON.stringify({'productId':productId, 'action':action})
		})
		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    console.log('Data:', data)
		    location.reload()
		});
}
