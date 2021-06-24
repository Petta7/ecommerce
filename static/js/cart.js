//запрашиваю все кнопки по классу корзины обновлений в cart.js и добавляю обработчик событий в цикле.
var updateBtns = document.getElementsByClassName('update-cart')

for (i = 0; i < updateBtns.length; i++) {
	updateBtns[i].addEventListener('click', function(){
		var productId = this.dataset.product
		var action = this.dataset.action
		console.log('productId:', productId, 'Action:', action)
		console.log('USER:', user)
//		создаю оператор if внутри cart.js и консольем пользователя и два разных оператора в зависимости от того,
//      вошел ли пользователь в систему или нет

		if (user == 'AnonymousUser'){
			addCookieItem(productId, action)
		}else{
			updateUserOrder(productId, action)
		}
	})
}

//Функция addCookieItem, как и updateUserOrder (), примет «productId» и «действие» в качестве параметров и будет запускаться
//при первом условии в нашем операторе «if». Далее добавляем и уменьшаем количество товара

function addCookieItem(productId, action){
	console.log('User is not authenticated')

	if (action == 'add'){
		if (cart[productId] == undefined){
		cart[productId] = {'quantity':1}

		}else{
			cart[productId]['quantity'] += 1
		}
	}

	if (action == 'remove'){
		cart[productId]['quantity'] -= 1

		if (cart[productId]['quantity'] <= 0){
			console.log('Item should be deleted')
			delete cart[productId];
		}
	}
	console.log('CART:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"
	location.reload()
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
				'X-CSRFToken':csrftoken,
			},
			body:JSON.stringify({'productId':productId, 'action':action})
		})
		.then((response) => {
		   return response.json();
		})
		.then((data) => {
		    location.reload()
		});
}