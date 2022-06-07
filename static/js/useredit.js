/*編集のバリデーション*/
function pushbutton() {
    const name = document.getElementById('first-name');
    const email = document.getElementById('email-address');
    const password = document.getElementById('password');
    const useredit = document.getElementById('useredit');
    const address = document.getElementById('address');
    const post = document.getElementById('post-code');
    const reg = /^[A-Za-z0-9]{1}[A-Za-z0-9_.-]*@{1}[A-Za-z0-9_.-]{1,}.[A-Za-z0-9]{1,}$/
    const postcode = /^\d{3}-?\d{4}$/
    var isError = false

    if (name.value === '' || name.value == null) {
        isError = true;
        document.getElementById('errorname').innerHTML = "名前を入力してください";
    }
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
    if (postcode.test(post.value) === false) {
        isError = true
        document.getElementById('errorpost').innerHTML = "郵便番号の値が正しくありません"
    }
    if (address.value === '' || address.value == null) {
        isError = true
        document.getElementById('erroraddress').innerHTML = "住所を入力してください";
    }
    if (isError) {
        return false;
    }
};