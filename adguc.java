import javax.crypto.Cipher;
import javax.crypto.SecretKeyFactory;
import java.util.Base64;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;
import java.io.ByteArrayOutputStream;
import java.security.SecureRandom;
import java.util.Arrays;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;

class McDonaldsCoupon {

    public static String date() {
        SimpleDateFormat localSimpleDateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSSSSSS'Z'", Locale.US);
        localSimpleDateFormat.setTimeZone(TimeZone.getTimeZone("UTC"));
        return localSimpleDateFormat.format(new Date(Long.valueOf(new Date().getTime() + Long.valueOf(2).longValue()).longValue()));
    }

    public static String Plexure_Key(String paramString1, String paramString2 ) {
        try {
            Base64.Encoder enc = Base64.getEncoder();
            byte[] arrayOfByte = new byte[8];
            new SecureRandom().nextBytes(arrayOfByte);
            PBEKeySpec key = new PBEKeySpec(paramString2.toCharArray(), arrayOfByte, 100, 384);
            byte[] secretKey = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1").generateSecret(key).getEncoded();
            SecretKeySpec localSecretKeySpec = new SecretKeySpec(Arrays.copyOfRange(secretKey, 0, 32), "AES");
            Cipher localCipher = Cipher.getInstance("AES/CBC/PKCS5PADDING");
            localCipher.init(1, localSecretKeySpec, new IvParameterSpec(Arrays.copyOfRange(secretKey, 32, 48)));
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            baos.write(localCipher.doFinal(paramString1.getBytes("UTF-8")));
            baos.write(arrayOfByte);
            return  enc.encodeToString(baos.toByteArray()).replace("\n", "").replace(" ", "");
        } catch (Exception err) {
            err.printStackTrace();
        }
        return null;
    }

}

class Main {
    public static void main (String[] args) {
        String AuthKey = "d4eee068-272a-4aec-9681-5e16dcef6fbd";
        System.out.println(McDonaldsCoupon.Plexure_Key(AuthKey + "|" + McDonaldsCoupon.date(), args[0]));
    }
}
