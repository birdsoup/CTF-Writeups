We're given the following source code:
```php
<?php
if (isset($_GET['src']))
    highlight_file(__FILE__) and die();
if (isset($_GET['md5']))
{
    $md5=$_GET['md5'];
    if ($md5==md5($md5))
        echo "Wonderbubulous! Flag is ".require __DIR__."/flag.php";
    else
        echo "Nah... '",htmlspecialchars($md5),"' not the same as ",md5($md5);
}

?>
<p>Find a string that has a MD5 digest equal to itself!</p>
<form>
    <label>Answer: </label>
    <input type='text' name='md5' />
    <input type='submit' />
</form>

<a href='?src'>Source Code</a>
```
We see that the md5's are compared with == instead of ===, which makes them vulnerable to type juggling vulnerabilities. 
In particular, if two strings both start with "0e" and contain numbers afterward, the == operator will always return that they're true. (Both get casted to integers of the form 0 * e ^{the remaining string}, so it returns 0 == 0).

To solve this, I just wrote a quick PHP script to generate strings of this form until one hashed to a hash of this form.

```php
<?php
echo "running script";
 $base = "0e";
 $result = "";
 $curr_number = 0; 
 do {
  $curr = $base . "$curr_number";
  $result = md5($curr);
  $curr_number += 1;
  }
 while ($curr == $result);
echo "\n";
echo $curr;
echo "\n";
echo $result;
echo "\n";
```

After leaving this running for a few minutes, it finds a solution, which gives us the flag when entered on the page.
