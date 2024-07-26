<?php
$servername = "localhost";
$username = "webapp";
$password = "password";
$dbname = "testdb";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $user = $_POST['username'];
    $pass = $_POST['password'];
    
    $sql = "SELECT * FROM users WHERE username = '$user' AND password = '$pass'";
    $result = $conn->query($sql);
    
    if ($result->num_rows > 0) {
        echo "Login successful! The flag is: FLAG{secret_flag}";
    } else {
        echo "Invalid username or password.";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <style>
        .custom-bg {
            background-color: rgb(30, 30, 30);
        }
        .custom-green {
            background-color: rgb(40, 163, 21);
        }
        .custom-green:hover {
            background-color: rgb(30, 143, 15);
        }
    </style>
</head>
<body class="custom-bg text-white">
    <div class="p-10">
        <h1 class="mb-8 font-extrabold text-4xl">Login</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <form method="POST">
                <div>
                    <label class="block font-semibold" for="username">Username</label>
                    <input class="w-full shadow-inner bg-gray-800 rounded-lg placeholder-gray-500 text-2xl p-4 border-none block mt-1" id="username" type="text" name="username" required="required" autofocus="autofocus">
                </div>
                <div class="mt-4">
                    <label class="block font-semibold" for="password">Password</label>
                    <input class="w-full shadow-inner bg-gray-800 rounded-lg placeholder-gray-500 text-2xl p-4 border-none block mt-1" id="password" type="password" name="password" required="required" autocomplete="new-password">
                </div>
                <div class="flex items-center justify-between mt-8">
                    <button type="submit" class="flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white custom-green md:py-4 md:text-lg md:px-10">Login</button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
