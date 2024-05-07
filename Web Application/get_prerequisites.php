<?php
// Connect to your database (update with your credentials)
$servername = "localhost";
$username = "root";
$password = "atharva";
$dbname = "student_prerequisites";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$studentID = $_POST['studentID'];

// Fetch courses and prerequisites data
$query = "SELECT DISTINCT C.CourseID, C.CourseName FROM courses C JOIN student_courses S ON S.PrerequisiteCourseID = C.CourseID WHERE S.StudentID = '$studentID';";

$result = $conn->query($query);

$prerequisites = array();
while ($row = $result->fetch_assoc()) {
    $prerequisites[] = $row;
}

// Close the database connection
$conn->close();

// Send data as JSON
header('Content-Type: application/json');
echo json_encode($prerequisites);
?>