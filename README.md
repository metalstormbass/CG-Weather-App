# CG-Weather-App - Cloudguard Workload Demo

Written by Michael Braun

![CI/CD](https://github.com/metalstormbass/CG-Weather-App/workflows/CI/CD/badge.svg?event=push) 


<p align="left">
    <img src="https://img.shields.io/badge/Version-1.0.0-green" />
</p>    

This document outlines how integrate Cloudguard Workloads with the Serverless framework in a CI/CD pipeline. This function uses the OpenWeatherMap API to return temperature values. <b> This demo simulates a compromised supply chain where a back door has been inserted into the function.</b>

![](images/function1.PNG)

This function is deployed through Github Actions. During the deployment, the function is scanned by Proact. Proact will examine the function and alert if there are any issues with the configuration. <br>

Function Self Protect (FSP) is also deployed in this demo. This provides runtime protection. There are two engines that work with FSP, a signature based engine, and a behavior based engine. 

<b> Get started by forking this repository! </b>

## Prerequisites

In order to run this demo, you need the following:

[Github Account](https://github.com) <br>
[AWS Account](https://aws.amazon.com) with API keys <br>
[Check Point Cloud Security Posture Management Account](https://dome9.com/) with API keys<br>
[OpenWeatherMap](https://https://openweathermap.org/api) - API Key<br>

You can also use this API key for OpenWeatherMap:

```d006ed318b33fd0baad3aec15369b3ab```

## Check Point CSPM Onboarding 

For this demo to work, you need to have your AWS account onboarded to Check Point CSPM. <b> Serverless Protection needs to be enabled. </b> The build will fail if these two requirements are not met. <br><br>

I've written an onboarding script to simplify this process. You must have AWS and CSPM API keys to run the script. Clone your repository and navigate to the scripts directory. Install the requirements.

```
pip install -r requirements.txt
```

Then run onboard.py. There are two options: <br>

1. Onboard AWS Account and Enable Serverless<br>

    - This will onboard an AWS account and enable serverless. Select this options if you have not already onboarded your AWS account.<br>
    
2. Enable Serverless on AWS Account <br>
    
    - This will enable Serverless Protection on an existing AWS account.<br> 


here is the sample output:

```
λ python onboard.py
Dome9 API Key: <enter API key here>
Dome9 Secret Key: <enter API Secret here>
AWS Access Key: <enter API key here>
AWS Secret Key: <enter API Secret here>
Select option:


        1. Onboard AWS Account and Enable Serverless
        2. Enable Serverless on AWS Account

Select a task number: 1
Friendly name of AWS account for Dome9: 
working . . .
Added Sucessfully
Serverless Protection Stage 1 Complete
Starting Stage 2. This will take some time.
Serverless Protection Stage 2 Complete.
Cloudguard ID: 
Finished!
```
## Prep the Github Environment

First go to Settings > Secrets and populate the secrets: <br>

![](images/secrets.png)

AWS_ACCESS_KEY_ID<br>
AWS_SECRET_ACCESS_KEY<br>
CG_TOKEN - <b>Note: This must be in the format CSPM_API_KEY:CSPM_API_SECRET</b> <br>

Second, select the "Actions" tab and enable workflows.

## Run the Build

To deploy this function to AWS, modifiy the _build_flag and commit the changes. This kicks off the Github Action. This will deploy the function. Once the build is finished, you will then see it in Check Point CSPM<br>

![](images/build.PNG)

Expand the "Deploy to AWS" tab and scroll to the bottom. You will see the Proact scan. Also, the results of the scan have been uploaded as artifacts. <b>Note the API gateway address.</b> This will be used for testing.<br>
![](images/build2.PNG)

## Enabling FSP
Navigate to the asset within CSPM.<br> 

To enable FSP, you must turn on "Auto-Protect" & "Block on Detect"

![](images/enablefsp1.PNG)

Once this is turned on, you must then redeploy the function. This can be done by rerunning the deployment pipeline. To do this from the CLI, you can run the following commands"

```
git commit -m "Deploy FSP" --allow-empty
git push
```

## Provisioning the FSP

In order for the function to be fully protected, the learning process must complete. This takes aproximately 3000 invocations. I have included a script that will perform this process. Ensure you enter real information as the function must be profiled with real activity. <br>

In the scripts directory, run profile.py. <br> 

Target: Input the api gateway address that you noted earlier. <br>
City: Enter any real city. <br>
API Key: Input your Api Key or use this: ```d006ed318b33fd0baad3aec15369b3ab```


Here is what it looks like:

```
.\profile.py
Weather App - Lambda Function
Target: <insert-api-gateway-here
City: Kelowna
API Key: d006ed318b33fd0baad3aec15369b3ab
Working
.
.
```
Keep an eye on the CSPM 