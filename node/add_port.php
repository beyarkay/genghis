<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$cwd = getcwd();
$genghis_dir = implode("/", array_slice(explode("/", $cwd), 0, -1));

# add the incoming dictionary to file, for the judge system to validate and integrate into the game
$data = file_get_contents('php://input');

echo count(array_keys((array)$data));
if (count((array)$data)) {
    $path = $genghis_dir.'/logs/'.date("c").'.json';
    
    $file_handle = fopen($path, 'w');
    fwrite($file_handle, $data);
    fclose($file_handle);
    
    # Change permissions on the file so the judge system can clean up later
    chmod($path, 0777);
    
    # log the operation to file, for auditing purposes
    $log_dir = $genghis_dir.'/logs/requests.log';
    $log = PHP_EOL.date("c").$data.PHP_EOL;
    file_put_contents($log_dir, $log, FILE_APPEND);

} else {
    echo "POST object is empty";
}
?>
