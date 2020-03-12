<?php
$student_number = escapeshellarg($_POST['student_number']);
$cmd = 'python3 bouncer.py '.$student_number.' 2>&1'; 
system($cmd, $retval);
?>
