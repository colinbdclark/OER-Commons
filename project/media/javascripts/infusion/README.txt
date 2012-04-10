
This version of Infusion was created from 

    https://github.com/amb26/infusion/tree/FLUID-4531
    commit a84ee84008399eb95ef4c714b99a5e5102ac28c3

using the following custom build command:

    ant customBuild -Dinclude="uiOptions, uploader, tooltip" -lib lib/rhino -Dexclude="jQuery" -DnoMinify="true"

"uploader" and "tooltip" components are added for the proper functioning of the video player.

Any unnecessary files have been removed from this folder.

