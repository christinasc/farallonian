<h2>Farallon Utilities: Python instance on Amazon Elastic Beanstalk </h2>

<h4>Purpose:</h4>
<ul>
<li> to get water bill info, pge info by logging in automatically and pulling data.
<li> remind people to submit online payment (unfortunately there is no auto pay option, old website for water utilities)
<li> forward bill info to housemates and remind them of what portion is due.
</ul>

<h4>Todo Items:</h4>
<ul>
<li> get Recology bill
<li> reminder to submit payment by txt message or slack integration
</ul>

<h4> Details:</h4>
<ul>
<li> Code location: https://github.com/christinasc/farallonian
<li> 64bit Amazon Linux 2016.09 v2.3.0 running Python 2.7
<li> Utilitizes Google API for Gmail - PGE.com website is a pain to webscrape so pulled email instead for parsing data
<li> pycrypto for handling file encryption. for more details see: http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto

</ul>