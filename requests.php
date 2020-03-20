<?php
$student_number = escapeshellarg($_POST['student_number']);
$cmd = 'python3 bouncer.py '.$student_number.' 2>&1'; 
$result = system($cmd, $retval);
$log = 'DATE: '.date("c").': '.$cmd.PHP_EOL.'    '.$result.PHP_EOL;
file_put_contents('./php_requests.log', $log, FILE_APPEND);
echo $log;
?>
