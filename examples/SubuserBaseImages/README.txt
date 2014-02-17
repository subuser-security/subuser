To use this examples wou will have to copy the required once to the subuser/programsThatCanBeInstalled

firefox_libx11_libubuntu_precise: is a full version with an dependency tree like

firefox_libx11_libubuntu_precise
   |__libx11_libubuntu_precise
       |__libubuntu_precise
       
no other image is used.

This are just examples.

To improve upon:
check if sudo permissions are really needed in the 'MakeBaseImage.sh'

if you write your own: 'MakeBaseImage.sh' it must handle everything
no option is passed to it: so make sure it does correct subuser required tagging ect..




