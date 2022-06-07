/*loginのバリデーション*/
function pushbutton() {
    const email = document.getElementById('email-address');
    const password = document.getElementById('password');
    const login = document.getElementById('login');
    const reg = /^[A-Za-z0-9]{1}[A-Za-z0-9_.-]*@{1}[A-Za-z0-9_.-]{1,}.[A-Za-z0-9]{1,}$/
    var isError = false;

    if (email.value === '' || email.value == null) {
        isError = true
        document.getElementById('errormsg').innerHTML = "メールアドレスを入力してください";
    } else if (!reg.test(email.value)) {
        isError = true
        document.getElementById('errormsg').innerHTML = "正しいメールアドレスを入力してください";
    }
    if (password.value === '' || password.value == null) {
        isError = true
        document.getElementById('errorpass').innerHTML = "パスワードを入力してください";
    }
    if (isError) {
        return false;
    }

};