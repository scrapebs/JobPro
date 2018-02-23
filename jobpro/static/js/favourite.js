function favourite() {
                var Vacancy = "{{ vacancy }}"
                $.ajax({
                    type:"POST",
                    url: "{% url 'vacancy_favourite_change' %}", 
                    cache: false,
                    data: {
                        "Vacancy": Vacancy, 'csrfmiddlewaretoken':"{{ csrf_token }}"
                    },
                    success: function(data) {
                    	 if (data == 'add'){
		                    document.getElementById('save').value='Убрать из избранного'
		                }
                        if (data == 'remove'){
                            document.getElementById('save').value='В избранное'
                        }
                    },
                    failure: function(data) { 
                        alert('Got an error dude');
                    }
                });
            }