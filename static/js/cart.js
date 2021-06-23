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
            console.log('User is authenticated, sending data...')
}

	})
}

