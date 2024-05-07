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
$query = "SELECT C.CourseID, C. CourseName from courses C where CourseID NOT IN (SELECT prerequisites.CourseID FROM prerequisites INNER JOIN student_courses ON student_courses.PrerequisiteCourseID = prerequisites.PrerequisiteCourseID WHERE student_courses.StudentID = '$studentID');";

$result = $conn->query($query);

$courses = array();
while ($row = $result->fetch_assoc()) {
    $courses[] = $row;
}

// Close the database connection
$conn->close();

// Send data as JSON
header('Content-Type: application/json');
echo json_encode($courses);
?>