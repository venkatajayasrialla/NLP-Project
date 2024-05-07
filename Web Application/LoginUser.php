<?php
// Assuming you have a MySQL database connection
$servername = "localhost";
$username = "root";
$password = "atharva";
$dbname = "student_prerequisites";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get username and password from the POST request
$data = json_decode(file_get_contents("php://input"));
$username = $data->username;
$password = $data->password;

// Validate the user credentials against the MySQL database
$sql = "SELECT StudentID FROM students WHERE Email = '$username' AND Password = '$password'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // Authentication successful
    $row = $result->fetch_assoc();
    $response = array('StudentID' => $row['StudentID']);
} else {
    // Authentication failed
    $response = array('error' => 'Invalid username or password');
}

// Close the database connection
$conn->close();

// Send the JSON response
header('Content-Type: application/json');
echo json_encode($response);
?>