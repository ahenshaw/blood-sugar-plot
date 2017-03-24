from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def getLatest(searchstring):
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.LocalWebserverAuth()
        # Refresh them if expired
        #~ gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)

    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    files = [f for f in file_list if searchstring in f['title']]
    files.sort(key=lambda x:x['modifiedDate'])
    data = files[-1].GetContentString()
    return data

if __name__ == '__main__':
    print(getLatest('Blood sugar'))
    